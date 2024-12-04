variable "traefik_records" {
  description = "Traefik records"
  type = list(string)
}

variable "domain" {
  description = "Primary domain"
  type = string
  default = "q.t"
}

variable "traefik_ip" {
  description = "Traefik ip address"
  type = string
}
