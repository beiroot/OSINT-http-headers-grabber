import requests
import csv
import datetime
import logging

# LOGGING
logger = logging.getLogger("OSINT-http-headers")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("OSINT-http-header.log")
fh.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(log_format)
logger.addHandler(fh)

# LIST OF HEADERS YOU WAN TO GRAB
headers_list = ["content-security-policy",
                "x-frame-options",
                "x-xss-protection",
                "x-content-type-options",
                "referrer-policy"]

csv_headers = ["domain", "url", "redirect", "to", "error"]
csv_rows = {}
TIMEOUT = 5

# TO GENERATE ALL THE URLS FOR CHECKING
protocols = ["http://",
             "https://",
             "http://www.",
             "https://www."]

# VARS
domains_to_visit = []
links_to_visit = []
visited_links = []

data = datetime.datetime.now().strftime("%Y-%m-%d")


# GENERATE URLs FROM A DOMAIN
def prepare_link(domain_to_prepare):
    for protocol in protocols:
        if domain_to_prepare.startswith("http"):
            link = domain_to_prepare
            if {domain_to_prepare: link} not in links_to_visit:
                links_to_visit.append({domain_to_prepare: link})
            break
        elif domain_to_prepare.startswith("www"):
            link = protocol.strip("www.") + domain_to_prepare
        else:
            link = protocol + domain_to_prepare

        if {domain_to_prepare: link} not in links_to_visit:
            links_to_visit.append({domain_to_prepare: link})
    return


# READ THE DOMAINS FROM THE FILE
def read_domains(filename):
    with open(filename) as file:
        for line in file:
            domains_to_visit.append(line.strip())


# WELL, LOG ERRORS :)
def log_error(err_domain, err_link):
    logger.error(f"Could not connect to: {err_link}")
    csv_rows["domain"] = err_domain
    csv_rows["url"] = err_link
    csv_rows["error"] = True
    writer.writerow(csv_rows)
    csv_rows.clear()


# DO THE ACTUAL REQUEST AND FOLLOW REDIRECTS
def request_link(r_domain, r_link):
    try:
        if r_link not in visited_links:
            r = requests.head(r_link, timeout=TIMEOUT)
            visited_links.append(r_link)
            logger.info(
                f"Response: {r_link} : {r.status_code}, is_redirect: {r.is_redirect}, "
                f"is_permanent_reddirect: {r.is_permanent_redirect}")

            if r.ok:
                # FOLLOW REDIRECTS
                if r.status_code in (300, 301, 302, 303, 304, 305, 306, 307, 308):
                    logger.info(
                        f"Response: {r_link} redirected to: {r.next.url}")

                    n_link = r.next.url.rstrip("/")

                    if {r_domain: n_link} not in links_to_visit:
                        links_to_visit.append({r_domain: n_link})

                    csv_rows["to"] = n_link
                    csv_rows["domain"] = r_domain
                    csv_rows["redirect"] = True
                    logger.info(f"Response: {r.url} : {r.status_code}")
            else:
                log_error(r_domain, r_link)
                return
            return r_domain, r_link, r
    except (ConnectionResetError, requests.Timeout, requests.ConnectionError, requests.exceptions.InvalidURL):
        log_error(r_domain, r_link)
    return


# PARSE THE HEADERS GRABBING THE ONES I WANT
def parse_results(domain_to_parse, link_to_parse, result_to_parse):
    csv_rows["domain"] = domain_to_parse
    csv_rows["url"] = link_to_parse

    headers = result_to_parse.headers
    for key, value in headers.items():
        key_insensitive = key.casefold()
        if key_insensitive in headers_list:
            csv_rows[key_insensitive] = value

    writer.writerow(csv_rows)
    csv_rows.clear()
    return


if __name__ == '__main__':
    with open("results-" + data + ".csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)

        # ADD HEADERS
        for header in headers_list:
            csv_headers.append(header)
        writer.writeheader()

        # READ IN THE DOMAINS FROM FILE
        read_domains("domains.txt")

        # GENERATE URLS
        for domain in domains_to_visit:
            prepare_link(domain)

        # VISIT EVERY URL
        for pair in links_to_visit:
            for key_domain, value_link in pair.items():
                requested_domain = key_domain
                requested_link = value_link

                # LOG
                logger.info("----------------------")
                logger.info(f"Domain: {requested_domain}, URL: {requested_link}")

                # REQUEST
                f_res = request_link(requested_domain, requested_link)
                if f_res is not None:
                    domain_res, link_res, r_res = f_res

                    # PARSE THE RESULT
                    parse_results(domain_res, link_res, r_res)
