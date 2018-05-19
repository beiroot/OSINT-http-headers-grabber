This small script is for parsing http-headers.
It is useful if you want to check you domains for CSP or x-headers (x-frame-options, x-xss-protection etc.) but it will grab any header.

Paste you domains into domains.txt line by line
github.com
reddit.com
...
# It can be www.something.com
# or http://www.something.com
# or https://something.com
# doesn't really matter, it will take care of various links :)


Just paste the headers you want to check (case insensitive)
headers_list = ["content-security-policy",
                "x-frame-options",
                "x-xss-protection",
                "x-content-type-options",
                "referrer-policy"]

The script will generate a list of links using:
protocols = ["http://",
             "https://",
             "http://www.",
             "https://www."]

It will also take care of redirects and inform you about them with a flag {redirected: True} and {to: link}. If the url doesn't respond (4xx or 5xx), the out will be {error: True}

The output is a csv file nicely sorted by domain name for all links
domain,url,redirect,to,error,content-security-policy,x-frame-options,x-xss-protection,x-content-type-options,referrer-policy
github.com,http://github.com,True,https://github.com,,,,,,
github.com,https://github.com,,,,default-src 'none'; base-uri 'self'; block-all-mixed-content; connect-src 'self' uploads.github.com status.github.com collector.githubapp.com api.github.com www.google-analytics.com github-cloud.s3.amazonaws.com github-production-repository-file-5c1aeb.s3.amazonaws.com github-production-upload-manifest-file-7fdce7.s3.amazonaws.com github-production-user-asset-6210df.s3.amazonaws.com wss://live.github.com; font-src assets-cdn.github.com; form-action 'self' github.com gist.github.com; frame-ancestors 'none'; frame-src render.githubusercontent.com; img-src 'self' data: assets-cdn.github.com identicons.github.com collector.githubapp.com github-cloud.s3.amazonaws.com *.githubusercontent.com; manifest-src 'self'; media-src 'none'; script-src assets-cdn.github.com; style-src 'unsafe-inline' assets-cdn.github.com,deny,1; mode=block,nosniff,"origin-when-cross-origin, strict-origin-when-cross-origin"
github.com,http://www.github.com,True,https://www.github.com,,,,,,
github.com,https://www.github.com,True,https://github.com,,,,,,

Hope you'll find it useful.

# TO DO
- argparse 
	* for grabbing all headers, not just the ones mentioned in headers_list
	* for using other file than domains.txt
