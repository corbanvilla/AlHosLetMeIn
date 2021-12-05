using UnityEngine;

using System;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Runtime.InteropServices.WindowsRuntime; // AsBuffer()

#if ENABLE_WINMD_SUPPORT
using Windows.Media;
using Windows.Media.Capture;
using Windows.Media.MediaProperties;
using Windows.Storage.Streams;
using Windows.Graphics.Imaging;  // Softwarebitmap

#endif

/// Corban Class
[Serializable]
public class AlhosnFaceBox
{
    public int Height { get; set; }
    public int Width { get; set; }
    public int X { get; set; }
    public int Y { get; set; }
    public string Alhosn { get; set; }

}

public class CameraStream : MonoBehaviour
{

    /// Initialization 
    /// 
    /// HTTP Client
    static HttpClient client = new HttpClient();

    /// <summary>
    /// Holds the current scenario state value.
    /// </summary>
    private ScenarioState currentState = ScenarioState.Streaming;

#if ENABLE_WINMD_SUPPORT

    /// <summary>
    /// References a MediaCapture instance; is null when not in Streaming state.
    /// </summary>
    private MediaCapture mediaCapture;

    /// <summary>
    /// Cache of properties from the current MediaCapture device which is used for capturing the preview frame.
    /// </summary>
    private VideoEncodingProperties videoProperties;

#endif

    private enum ScenarioState
    {
        Idle,
        Streaming
    }

    /// <summary>
    ///  Time to sleep between each frame being streamed (0.1f = 1/10th of a second = ~1/3 frames are processed)
    /// </summary>
    private float sleep = 0.1f;


    // Start is called before the first frame update
    async void Start()
    {
        // Setup our camera / settings
        await StartWebcamStreamingAsync();

        // Start thread to read from camera buffer and send to API
        StartCoroutine("StreamLoop");

    }

    // Update is called once per frame
    ///void Update()
    ///{
        // We don't necessarily need to call anything here since everything is
        // executed through the coroutine.
    ///}

    IEnumerator StreamLoop()
    {

        for (;;)
        {

            if (this.currentState != ScenarioState.Streaming)
            {
                yield return new WaitForSeconds(sleep);
            }

            // Call async method to stream video frame
            // TODO - consider adding stopwatch to check when this finishes
            var task = Task.Run(ProcessCurrentVideoFrameAsync);


            // TODO - test on api bad status / response
            yield return new WaitUntil(() => task.IsCompleted);

        }
    }


    async void OnApplicationQuit()
    {
        StopCoroutine("StreamLoop");
        await ShutdownWebcamAsync();
    }

    private async Task<bool> StartWebcamStreamingAsync()
    {
        bool successful = false;

        try
        {

#if ENABLE_WINMD_SUPPORT

            // SETUP Backend connection
            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));

            this.mediaCapture = new MediaCapture();

            // For this scenario, we only need Video (not microphone) so specify this in the initializer.
            // NOTE: the appxmanifest only declares "webcam" under capabilities and if this is changed to include
            // microphone (default constructor) you must add "microphone" to the manifest or initialization will fail.
            MediaCaptureInitializationSettings settings = new MediaCaptureInitializationSettings();
            settings.StreamingCaptureMode = StreamingCaptureMode.Video;
            await this.mediaCapture.InitializeAsync(settings);
            this.mediaCapture.Failed += this.MediaCapture_CameraStreamFailed;

            // Cache the media properties as we'll need them later.
            var deviceController = this.mediaCapture.VideoDeviceController;
            this.videoProperties = deviceController.GetMediaStreamProperties(MediaStreamType.VideoPreview) as VideoEncodingProperties;

#endif

            successful = true;
        }
        catch (Exception ex)
        {
            Debug.Log("Unable to initialize properly!");
        }

        return successful;
    }
    
    private async Task ProcessCurrentVideoFrameAsync()
    {

#if ENABLE_WINMD_SUPPORT

        // Create a VideoFrame object specifying the pixel format we want our capture image to be (NV12 bitmap in this case).
        // GetPreviewFrame will convert the native webcam frame into this format.
        const BitmapPixelFormat InputPixelFormat = BitmapPixelFormat.Nv12;
        using (VideoFrame previewFrame = new VideoFrame(InputPixelFormat, (int)this.videoProperties.Width, (int)this.videoProperties.Height))
        {
            try
            {
                await this.mediaCapture.GetPreviewFrameAsync(previewFrame);
            }
            catch (Exception)
            {
                Debug.Log("Unable to get frame from camera!");
                return;
            }

            IList<AlhosnFaceBox> faces;
            try
            {

                SoftwareBitmap convertedBitmap = SoftwareBitmap.Convert(previewFrame.SoftwareBitmap, BitmapPixelFormat.Rgba16); // TODO - try with rgba8 and smaller encoded jpgs

                byte[] image_bytes = await EncodedBytes(convertedBitmap, BitmapEncoder.JpegEncoderId);

                string image_b64 = Convert.ToBase64String(image_bytes);
                string request_json = JsonUtility.ToJson(new { image = image_b64 });

                var response = await client.PostAsync(
                    "http://192.168.137.1:80/faces",
                    new StringContent(request_json, Encoding.UTF8, "application/json")
                );
                string responseContent = await response.Content.ReadAsStringAsync();

                faces = JsonUtility.FromJson<IList<AlhosnFaceBox>>(responseContent);
                
                Debug.Log("Made request!");

            }
            catch (Exception ex)
            {
                Debug.Log("Error occurred getting faces!");
                return;
            }

            // Create our visualization using the frame dimensions and face results but run it on the UI thread.

        }

#endif

    }

    private async Task ShutdownWebcamAsync()
    {

#if ENABLE_WINMD_SUPPORT

        if (this.mediaCapture != null)
        {
            if (this.mediaCapture.CameraStreamState == Windows.Media.Devices.CameraStreamState.Streaming)
            {
                try
                {
                    await this.mediaCapture.StopPreviewAsync();
                }
                catch (Exception)
                {
                    ;   // Since we're going to destroy the MediaCapture object there's nothing to do here
                }
            }
            this.mediaCapture.Dispose();
        }

        this.mediaCapture = null;

#endif
        
    }

#if ENABLE_WINMD_SUPPORT

    // Handles stream failures
    private void MediaCapture_CameraStreamFailed(MediaCapture sender, object args)
    {
        Application.Quit();
    }

    private async Task<byte[]> EncodedBytes(SoftwareBitmap soft, Guid encoderId)
    {
        byte[] array = null;

        // First: Use an encoder to copy from SoftwareBitmap to an in-mem stream (FlushAsync)
        // Next:  Use ReadAsync on the in-mem stream to get byte[] array

        using (var ms = new InMemoryRandomAccessStream())
        {
            BitmapEncoder encoder = await BitmapEncoder.CreateAsync(encoderId, ms);
            encoder.SetSoftwareBitmap(soft);

            try
            {
                await encoder.FlushAsync();
            }
            catch (Exception ex) { return new byte[0]; }

            array = new byte[ms.Size];
            await ms.ReadAsync(array.AsBuffer(), (uint)ms.Size, InputStreamOptions.None);
        }
        return array;
    }

#endif

}
