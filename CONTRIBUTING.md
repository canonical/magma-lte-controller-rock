# Contributing

## Build and deploy

```bash
rockcraft pack -v
sudo skopeo --insecure-policy copy oci-archive:magma-lte-controller_1.6.1_amd64.rock docker-daemon:magma-lte-controller:1.6.1
docker run magma-lte-controller:1.6.1
```
