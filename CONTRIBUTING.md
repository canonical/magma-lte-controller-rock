# Contributing

## Build and deploy

```bash
rockcraft pack -v
sudo skopeo --insecure-policy copy oci-archive:magma-lte-controller_1.8.0_amd64.rock docker-daemon:magma-lte-controller:1.8.0
docker run magma-lte-controller:1.8.0
```
