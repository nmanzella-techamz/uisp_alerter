# UISP Alerter

## Description
Send mail messages when [UISP](https://help.ui.com/hc/en-us/articles/115012196527-UISP-First-Time-Setup-Installation) (Ubiquiti Internet Service Provider) detects an outage.

## Prerequisites
- UISP server.
- Mail server that accepts SMTP authentication using a password.
- Linux server or Windows server with WSL2 installed.
- Docker Compose installed on your server.

## Setup
1. On your UISP server, generate an API key. Using the UISP web interface go to "Settings" > "Users" > "Create new API token" button.  Choose "Read Only" access.  Record this key in a secure location. 
2. Log into the Linux server you wish to run UISP Alerter, open a terminal, navigate to a directory should contain the UISP Alerter files, and run `git clone https://github.com/nmanzella-techamz/uisp_alerter.git`.  
3. In the "uisp_alerter/volumes" directory, make a copy of "default.config.toml" and rename the copy "config.toml".
4. Edit "config.toml" so that you specify information about your UISP server, your mail server, and UISP sites you wish to receive alerts about.  You can configure multiple alerts in the "config.toml".   
5. Edit crontab with `crontab -e` and add the following line: `0 12 * * * docker compose -f /path/to/uisp_alerter/compose.yaml up -e SITE_CONFIG_ID=id_specified_in_a_site_config_in_config.toml`  Edit the schedule, path to "compose.yaml", and SITE_CONFIG_ID (should correspond to a valid "site_configs.id" in the "config.toml" file) as appropriate.  This will run the UISP Alerter Docker container on your preferred schedule.  Add as many lines to crontab as necessary if you wish to receive alerts on different schedules, different sites, etc.

## Notes
If you use the setting "ignore_alerts_less_than" in "config.toml", it is advisable to increase the "start_delta" and "end_delta" by the same amount of time (see below).  This will avoid situations where an outage starts within the desired timeframe but the outage has not continued for enough time for the UISP Alerter to determine if it should be ignored or not.

```toml
[[site_configs]]
...
ignore_alerts_less_than = 180 # Three minutes
[site_configs.start_delta] # One day, three minutes
days = 1
hours = 0
minutes = 3
seconds = 0
[site_configs.end_delta] # Three minutes
days = 0
hours = 0
minutes = 3
seconds = 0
```