import argparse
import asyncio
import logging

from av import VideoFrame

from loguru import logger as log

from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaRelay
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling

from face_stream import FaceStreamTrack


relay = MediaRelay()


async def run(pc, signaling, poll_interval):

    # connect signaling
    await signaling.connect()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log.info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            log.error("Cleaning up connection.....")
            await pc.close()

    @pc.on("track")
    def on_track(track):
        log.info("Receiving %s" % track.kind)

        if track.kind == "video":
            log.debug("Setting up proxy stream for analysis")
            pc.addTrack(
                FaceStreamTrack(
                    relay.subscribe(track)
                )
            )

    # consume signaling
    while True:

        # Get our request from client
        obj = await signaling.receive()

        if obj:
            log.debug(f'Message Received: {obj}')

        if isinstance(obj, RTCSessionDescription):
            # Set the remote description to offer specs
            log.info("Setting remote description....")
            await pc.setRemoteDescription(obj)

            if obj.type == "offer":
                # send answer
                log.info("Responding to offer and sending local description...")
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)

        elif isinstance(obj, RTCIceCandidate):
            log.debug("Adding ice candidate....")
            await pc.addIceCandidate(obj)

        elif obj is BYE:
            log.info("Exiting")
            break

        # Sleep between server polls
        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video stream from the command line")
    parser.add_argument("--verbose", "-v", action="count")
    parser.add_argument("--poll-interval", default=0.5, help="Time to sleep (seconds) between server polls")
    add_signaling_arguments(parser)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # create signaling and peer connection
    signaling = create_signaling(args)
    pc = RTCPeerConnection()

    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
                signaling=signaling,
                poll_interval=args.poll_interval,
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        # cleanup
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
