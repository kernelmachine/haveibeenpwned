# Have I Been Pwned?

Python interface to Have I Been Pwned API

## Recent Changes

0.0.5 - Things are now stable

## What is Have I Been Pwned?

[Have I Been Pwned](https://haveibeenpwned.com/) is a free resource to quickly assess if an account or domain has been compromised or "pwned" in a data breach. By aggregating the data here the project helps victims be aware of account compromises, and highlights the severity of the risks of Internet-wide attacks. For more information on who, what, and why, click [here](https://haveibeenpwned.com/About).

## Dependencies

```
requests
gevent
```

## Setup

This library runs on **Python 2.7-3.4**

To install, run:

```
$ pip install hibp
```

## To run

You can query breach data on individual accounts/domains as well as data on full breaches. Each service request object contains a response attribute that holds the raw data output in JSON format. To perform a query, just setup a service request object, and then execute:

```python
>> req = HIBP.get_account_breaches("pegasos1")
>> req.execute()
>> req.response
```

## What data do I see?

To give you an idea of the data you can see from this API, here are some example JSON outputs.

```python
>> req = HIBP.get_breach("adobe")
>> req.execute()
>> print(json.dumps(req.response, indent=4, sort_keys=True))
{
    "AddedDate": "2013-12-04T00:00:00Z",
    "BreachDate": "2013-10-04",
    "DataClasses": [
        "Email addresses",
        "Password hints",
        "Passwords",
        "Usernames"
    ],
    "Description": "In October 2013, 153 million Adobe accounts were breached with each containing an internal ID, username, email, <em>encrypted</em> password and a password hint in plain text. The password cryptography was poorly done and <a href=\"http://stricture-group.com/files/adobe-top100.txt\" target=\"_blank\">many were quickly resolved back to plain text</a>. The unencrypted hints also <a href=\"http://www.troyhunt.com/2013/11/adobe-credentials-and-serious.html\" target=\"_blank\">disclosed much about the passwords</a> adding further to the risk that hundreds of millions of Adobe customers already faced.",
    "Domain": "adobe.com",
    "IsActive": true,
    "IsRetired": false,
    "IsSensitive": false,
    "IsVerified": true,
    "LogoType": "svg",
    "Name": "Adobe",
    "PwnCount": 152445165,
    "Title": "Adobe"
}

```

```python
>> req = HIBP.get_domain_breaches("linkedin.com")
>> req.execute()
>> print(json.dumps(req.response, indent=4, sort_keys=True))
    {
        "AddedDate": "2016-05-21T21:35:40Z",
        "BreachDate": "2012-05-05",
        "DataClasses": [
            "Email addresses",
            "Passwords"
        ],
        "Description": "In May 2016, <a href=\"https://www.troyhunt.com/observations-and-thoughts-on-the-linkedin-data-breach\" target=\"_blank\">LinkedIn had 164 million email addresses and passwords exposed</a>. Originally hacked in 2012, the data remained out of sight until being offered for sale on a dark market site 4 years later. The passwords in the breach were stored as SHA1 hashes without salt, the vast majority of which were quickly cracked in the days following the release of the data.",
        "Domain": "linkedin.com",
        "IsActive": true,
        "IsRetired": false,
        "IsSensitive": false,
        "IsVerified": true,
        "LogoType": "svg",
        "Name": "LinkedIn",
        "PwnCount": 164611595,
        "Title": "LinkedIn"
    }
```

## Concurrent queries

If you want to query on multiple accounts or domains at once, you can use the `AsyncHIBP` object, which performs queries concurrently via gevent.

```python
>> names = ['adobe','ashleymadison', 'myspace']
>> breaches = [HIBP.get_breach(x) for x in names]
>> async_reqs = AsyncHIBP().map(breaches)
>> [async_req.response for async_req in async_reqs]
```

In addition to a canonical `map` method, `AsyncHIBP` also supports the `imap` method, which returns a generator object for lazy queries.


```python
>> domains = ['twitter.com','facebook.com', 'adobe.com']
>> breaches = [HIBP.get_domain_breaches(x) for x in domains]
>> async_reqs = AsyncHIBP().imap(breaches)
>> next(async_reqs)
```
