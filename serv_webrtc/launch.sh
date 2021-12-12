docker build . -t face_detection -f docker/Dockerfile.webrtc
docker run -it --gpus=all -p 80:80 -v $(pwd)/faces.db:/app/faces.db face_detection
