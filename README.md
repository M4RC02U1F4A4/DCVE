# CVEs DASHBOARD

![](doc/dashboard.png)

## Setup

1. `git clone https://github.com/M4RC02U1F4A4/DCVE.git`
2. `cd DCVE`
3. Edit the `docker-compose` file according to your preference
4. `docker-compose up --build -d`
> :warning: **First start** -> The first start may take a few minutes as the DB must be filled

## Guide
- `LAST 10 PUBLISHED` -> Last 10 CVEs published divided by severity
- `LAST 10 MODIFIED` -> Last 10 CVEs modified divided by severity
- `MODIFIED TODAY` -> All CVEs modified today
- `PUBLISHED TODAY` -> All CVEs published today
- `LAST 72h` -> All CVEs published or modified in the last 72h
- `CHECK CVE` -> All CVEs published or modified with the ability to "set as read" (click on the ID to remove it from the dashboard)
- `LAST 10 KEV` -> Last 10 Known Exploited Vulnerabilities
- `KEV TODAY` -> Known Exploited Vulnerabilities published today
- `PATCH TUESDAY` -> Last published Microsoft Patch Tuesday
- `FAST TUESDAY` -> Only CVEs with scores higher or equal than 7 on Microsoft's latest Patch Tuesday