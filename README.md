# RITA Integration with Splunk
As you know, [RITA](https://github.com/activecm/rita) is an open-source framework for network traffic analysis. Using this repository, you can integrate RITA with Splunk.\
By doing this, all of RITA's analyses will be sent to Splunk, and you can use all the data received from RITA in Splunk for correlation purposes.

To perform this integration, the project is divided into two parts:\
**1-** Setting up RITA and configuring a secure, customized web server for RITA analysis data.\
**2-** Installing the necessary addons on Splunk to receive RITA data.

# RITA Side Configuration
## webserver  
Splunk uses `curl` to receive files, so a web server is needed to make all the feeds available via the web. (If you already have a web server and want to use it, you can skip this part.) This Python file runs as a service using `Webserver_Service.sh`.

**Note:** The web server is designed with security in mind, allowing only CSV files to be downloaded. Additionally, the output (statuses and information) displayed on the web server is fake, while the actual logs can be accessed at "var/log/Web_Server.log/".

- **Variables:**  
  **1-** `PORT`, which specifies the web server's port. By default, it uses port 8078.  
  **2-** `DIRECTORY`, which defines the web server's directory. By default, "/opt/Threatintel/" is used.  
  **3-** `REAL_LOG_FILE_PATH`, which defines the web server's log file path. By default, "var/log/Web_Server.log/" is used.  
  **4-** `ALLOWED_IPS`, which specifies the list of authorized IPs that can connect to the web server.\
  **5-** `RATE_LIMIT`, which limits the number of requests that can be made from a single IP address to 10 requests per second. If an IP address exceeds this limit, it will be temporarily blocked.\
  **6-** `BLOCK_DURATION`, which specifies the duration for which an IP address will be blocked if it exceeds the rate limit. In this case, the IP address will be blocked for 60 seconds.

**Implementation Steps:**  
**1-** First, create the following directories.

```
mkdir -p /root/scripts/
mkdir -p /opt/Threatintel
```

**2-** Then, use the following command to download the script files and move the file to the `scripts` directory.

```
wget https://github.com/Mohammad-Mirasadollahi/RITA-Integration-with-Splunk/releases/download/RITA-Splunk/webserver.tar.gz
mv webserver.tar.gz /root/scripts/
```

**3-** Extract the zip file using the command below, then delete the zip file.

```
cd /root/scripts/
tar xzvf webserver.tar.gz
rm -rf webserver.tar.gz
```

**4-** Finally, use the following commands to run the `webserver.py` service. (service name is Local_WebServer)

```
bash Webserver_Service.sh
```


## RITA  
In the first step, you must install RITA, which you can set up using [this link](https://github.com/activecm/rita).

After installing RITA, you need to configure it to analyze the Zeek logs in the following path (/opt/zeek/logs/current/) every hour using below command, and place the results in the specified path (/opt/Threatintel/RITA.csv).

```
echo "0 * * * * rita import --rolling --database=mydb --logs=/opt/zeek/logs/current/ && rita view --stdout mydb > /opt/Threatintel/RITA.csv && sed -i '1d' /opt/Threatintel/RITA.csv" | crontab -
```

  # Splunk Side Configuration

## Prerequisite 
You must first download and install the following Addon from the link below:\
https://splunkbase.splunk.com/app/635

## TA-RITA-Splunk
**Installation of TA-RITA-Splunk:**  
**1-** Download the TA file from the following link:
```bash
wget https://github.com/Mohammad-Mirasadollahi/RITA-Integration-with-Splunk/releases/download/RITA-Splunk/TA-RITA-Splunk.tar.gz
```

**2-** Transfer and extract the addon with the following commands (assuming the default Splunk installation path):
```
mv TA-RITA-Splunk.tar.gz /opt/splunk/etc/apps/
cd /opt/splunk/etc/apps/
tar xzvf TA-RITA-Splunk.tar.gz
rm -rf TA-RITA-Splunk.tar.gz
```

**Note:** Open the `savedsearches.conf` file inside the `TA-RITA-Splunk/default` folder and modify the IP in the `url` field according to your organization’s setup. This IP should be the Web Server IP that we set up in the previous step.\
**Note:** From `savedsearches.conf` you can change `cron_schedule` based on your RITA configuration. Default is every 10 minutes.

**3-** Finally, restart the Splunk:
```
/opt/splunk/bin/./splunk restart
```
**4-** RITA Data in Splunk:
From the search and reporting app, run the following command after the RITA file is downloaded.
```
| inputlookup rita_intel
```
