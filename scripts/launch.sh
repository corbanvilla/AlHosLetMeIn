docker build . -t face_detection -f docker/Dockerfile.api
docker run -it --gpus=all -p 80:80 -v $(pwd)/faces.db:/app/faces.db face_detection
