resource "aws_key_pair" "process-alpha" {
   key_name = "process-alpha"
   public_key = "${file("./keys/process-alpha.pem.pub")}"
}

resource "aws_instance" "client_instance_1_us_east_1a" {
  ami                         = "ami-07d0cf3af28718ef8"
  instance_type               = "t2.micro"
  key_name                    = "process-alpha"
  associate_public_ip_address = "true"
  private_ip                  = "10.10.0.10"
  subnet_id                   = "${aws_subnet.client_subnet_1.id}"
  vpc_security_group_ids      = ["${aws_security_group.client_security_group.id}"]

  root_block_device {
    volume_type           = "gp2"
    volume_size           = "24"
    delete_on_termination = true
  }

  tags = {
    Name = "client_instance_1_us_east_1a"
  }

#   user_data = "${data.template_cloudinit_config.client_cloudinit.rendered}"

  provisioner "file" {
    source      = "./init"
    destination = "/home/ubuntu"

    connection {
      host = "${self.public_ip}"
      type        = "ssh"
      user        = "ubuntu"
      private_key = "${file("./keys/process-alpha.pem")}"
    }
  }

  provisioner "remote-exec" {
    inline = [
      "sleep 10",
      "mv ./init/site/* .",
      "chmod +x ./init/boot-strap.sh",
      "./init/boot-strap.sh",
      "rm -rf ./init",
      "sudo docker-compose up -d",
      "sleep 10"
    ]

    connection {
      host = "${self.public_ip}"
      type        = "ssh"
      user        = "ubuntu"
      private_key = "${file("./keys/process-alpha.pem")}"
    }
  }

}


resource "aws_eip" "eip_manager" {
  instance = "${aws_instance.client_instance_1_us_east_1a.id}"
  vpc = true
  
  tags = {
    Name = "eip-client_instance_1_us_east_1a"
  }

#  lifecycle {
#    prevent_destroy = true
#  }
}





resource "aws_eip_association" "client_1_us_east_1a_eip" {
  instance_id   = "${aws_instance.client_instance_1_us_east_1a.id}"
  allocation_id = "${aws_eip.eip_manager.id}"
}
