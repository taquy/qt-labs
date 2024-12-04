terraform {
  required_providers {
    pihole = {
      source = "ryanwholey/pihole"
    }
  }
}

provider "pihole" {
  url = "http://dns.q.t"
  api_token = sha256(sha256("root1234"))
}
