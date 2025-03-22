# Authentication
credentials = "../credentials/tribal-bonsai-453807-i6-cc1e5bc2ee63.json"
# Project Settings
project_id = "tribal-bonsai-453807-i6"
region     = "asia-southeast1"   # Updated to Singapore region
zone       = "asia-southeast1-a" # Updated to a Singapore zone

# GKE Settings
machine_type_node = "n2-standard-2"

# Compute Instance Settings
instance_name         = "jenkins-server"
machine_type_instance = "e2-medium"
boot_disk_image       = "ubuntu-os-cloud/ubuntu-2004-lts"
boot_disk_size        = 50

# Network Settings
firewall_name = "jenkins-firewall"
