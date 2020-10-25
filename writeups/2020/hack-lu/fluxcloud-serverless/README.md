# [Hack.lu CTF 2020] Challenge - FluxCloud Serverless

[Instance](https://serverless.cloud.flu.xxx/demo/gdw7Iwv6LGPNeDes_dbDk/)

## Notes

- NodeJS Serverless App
- Source Code avalible
- Resets after around 10 attemps


Need to get to endpoint `/flag` but if the string `flag` is in the url, the "waf" activates and blocks the connection.

[Flag endpoint](https://serverless.cloud.flu.xxx/demo/f9wg4bDMV2QXTetl3UQ0x/flag)

Changes the endpoint

**Protected by middleware (waf)**

```javascript
const badStrings = [
    'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',
    'woyouyizhixiaomaol',
    'conglaiyebuqi',
    'UNION',
    'SELECT',
    'SLEEP',
    'BENCHMARK',
    'alert(1)',
    '<script>',
    'onerror',
    'flag',
];

function checkRecursive(value) {
    // don't get bypassed by double-encoding
    const hasPercentEncoding = /%[a-fA-F0-9]{2}/.test(value);
    if (hasPercentEncoding) {
        return checkRecursive(decodeURIComponent(value));
    }

    // check for any bad word
    for (const badWord of badStrings) {
        if (value.includes(badWord)) {
            return true;
        }
    }
    return false;
}

function isBad(req) {
    const toCheck = ['url', 'body'];
    for (const key of toCheck) {
        const value = req[key];
        if (!value) {
            continue;
        }
        if (checkRecursive(String(value))) {
            return key;
        }
    }
    return null;
}

// use named function for better logging
module.exports = async function waf(req, res, next) {
    const blockReason = isBad(req);
    if (blockReason !== null) {
        res.status(403);
        res.set('X-WAF-Blocked', blockReason);
        // internal redirect to /blocked so the app can show a custom 403 page
        req.url = '/blocked';
        return;
    }
};

```

## Thoughts

**Case Sensitivity**

- The broken version had an issue with case sensitivity
    - Changes from a `string includes` vs the new regex patterns (in 2.0)
