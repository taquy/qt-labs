resource "pihole_dns_record" "traefik_records" {
  for_each = toset(var.traefik_records)
  domain = "${each.value}.${var.domain}"
  ip     =  var.traefik_ip
}
