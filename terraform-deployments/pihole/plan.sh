#!/bin/bash

terraform plan -var-file=main.tfvars -out tf.plan

terraform apply -auto-approve tf.plan

