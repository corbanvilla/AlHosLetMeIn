using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Microsoft.MixedReality.WebRTC.Unity;

public class InitiateConnection : MonoBehaviour
{

    public NodeDssSignaler NodeDssSignaler;


    // Start is called before the first frame update
    void Start()
    {
        // Subscribe function to init event
        // NodeDssSignaler.PeerConnection.OnInitialized.AddListener(Connect);

    }

    public void Connect()
    {
        Debug.Log("Starting connection!");
        NodeDssSignaler.PeerConnection.StartConnection();
    }
    public void StartConnectionLoop()
    {
        // Attempt to initiate our connection
        // await Task.Delay(System.TimeSpan.FromSeconds(30));
        /* while (!NodeDssSignaler.PeerConnection.StartConnection())
         {
             Debug.Log("Sleeping while waiting for system...");
             await Task.Delay(System.TimeSpan.FromSeconds(3));

         }
         Debug.Log("Started connection!");*/

        // Start connection retry loop
        Debug.Log("Starting connection retry loop!");
        StartCoroutine(ConnectSDP());

    }

    public void StopConnectionLoop()
    {
        Debug.Log("Connection established! Ending retry loop...");
        StopCoroutine("ConnectSDP");
    }

    // Connection agent coroutine
    IEnumerator ConnectSDP()
    {
        Debug.Log("Attempting to start connection!");
        NodeDssSignaler.PeerConnection.StartConnectionIgnoreError();
        yield return new WaitForSeconds(3.0f);
    }

}
