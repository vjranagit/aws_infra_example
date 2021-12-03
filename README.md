## Setup
#### Domain Name
A free domain name "makstores.tk," created with www.freenom.com and associated to an elastic ip using a null A record, and a 'www' A record.

example site is temporarily available at https://www.makstores.tk
#### SSL
**Openssl** was used to create .crt, .key, and dhparm.pem files. It should be noted that self signed certificates are not generally accepted as a reliable and will produce a warning that the site is not trusted before  users are able to procede to the site. In practice something like **Certbot** (https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx) provided by **Lets Encrypt** (https://letsencrypt.org/getting-started/) would be more reliable.
###### Command for generating makstores.tk.crt  makstores.tk.key 
```bash
sudo openssl req -x509 -nodes -sha256 -days 365 \
			-newkey rsa:2048 \
			-keyout ./infra/init/site/nginx/ssl/makstores.tk.key \
			-out  ./infra/init/site/nginx/ssl/makstores.tk.crt
```
###### Command for generating dhparam.pem file
```bash
sudo openssl dhparam -out /etc/nginx/ssl/dhparam.pem 4096
```


###### to check health just simply run 
```bash
./health.sh <yourpublicIP>
```

## Design
#### Provisioning
Terreform scripts located at the top level directory provsision the following:
- Network
	- aws_vpc
	- aws_internet_gateway
	- aws_route_table
	- aws_subnet
	- aws_route_table_association
- Security
	- aws_security_group
- Instance
	- aws_instance:
	- aws_eip_association

#### Configuration
Instance Provisioners are called in "instance.tf" to configure the deployed ec2 instance in the following steps: 
- A *file provisioner* uses a .pem file to connect to the instance and scp all requisite files, scripts, and configurations contained in the local /init folder.
- A *remote-exec* provisioner is then used to extract all relevent configuration scripts into the appropriate location, and execute a bash script "boot-strap.sh" to configure dependencies on the server and run the docker network specified in /infra/init/docker-compose.yml

#### Operation
An alpine Nginx server running in a docker container proxies https requests on port 443 to a docker container running an alpine node.js server exposing port 80 for http requests on localhost.

## Notes on Deployment
- Elastic IP was generated prior to deployment and associated by id in instance.tf
- Domain Name was created using the free service provided by www.freenom.com
- SSL certificates generated for this project reference the generated domain.
- SSL certificates under /infra/site/nginx/ssl must be generated prior to execution
- SSL certificates are referenced by name in both boot-strap.sh and docker-compose.yml
- Existing aws .pem key is located in /infra/keys and refrenced in instance.tf

## Project Structure
```
/infra
	+ instance.tf
	+ network.tf
	+ provider.tf
	+ security.tf
 	/init
		+ boot-strap.sh
		/site
			+ docker-compose.yml
			/nginx
				+ default.conf
				/ssl
					+ makstores.tk.crt
					+ makstores.tk.key
					+ dhparam.pem
			/nodejs
				+ index.js
	/keys
		+ aws_instance_key.pem 
```