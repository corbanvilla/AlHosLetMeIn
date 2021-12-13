docker run -it --gpus=all $(pwd)/faces.db:/usr/src/app/faces.db $1 --remote-peer=hololens --signaling-host=10.7.0.3 --signaling-port=3000 --local-peer=face-api --verbose
