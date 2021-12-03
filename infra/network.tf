resource "aws_vpc" "client_vpc" {
  cidr_block           = "10.10.0.0/20"
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name = "client-vpc"
  }
}

resource "aws_internet_gateway" "client_gateway" {
  vpc_id = "${aws_vpc.client_vpc.id}"

  tags = {
    Name = "client_gateway"
  }
}

resource "aws_subnet" "client_subnet_1" {
  vpc_id            = "${aws_vpc.client_vpc.id}"
  cidr_block        = "10.10.0.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "client-subnet-1"
  }
}

resource "aws_route_table" "client_public_route" {
    vpc_id = "${aws_vpc.client_vpc.id}"
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.client_gateway.id}"
    }
    tags = {
        Name = "client-public-route"
    }
}

resource "aws_route_table_association" "client_subnet_1_route_association" {
    subnet_id = "${aws_subnet.client_subnet_1.id}"
    route_table_id = "${aws_route_table.client_public_route.id}"
}

