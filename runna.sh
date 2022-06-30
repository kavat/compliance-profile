#!/bin/sh

container=$(docker run -d --privileged compliance-profile)
docker exec -it $container /bin/bash
