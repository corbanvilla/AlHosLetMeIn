docker run -it --gpus=all -v $(pwd)/faces.db:/usr/src/app/faces.db $1 --remote-peer=hololens --signaling-host=10.225.39.94 --signaling-port=3000 --local-peer=face-api --signaling=node-dss
