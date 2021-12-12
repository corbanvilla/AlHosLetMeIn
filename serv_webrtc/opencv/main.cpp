//#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <iostream>
#include <opencv2/objdetect.hpp>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

using namespace std;
using namespace cv;

namespace py = pybind11;

struct FaceBox {
    int top_x;
    int top_y;
    int bottom_x;
    int bottom_y;
};

vector<FaceBox> get_face_locations(py::array_t<uint8_t>& img_in);
//vector<FaceBox> get_largest_face(Mat img);



vector<FaceBox> get_face_locations(py::array_t<uint8_t>& img_in) {

    // TODO - maybe make this a function
    auto rows = img_in.shape(0);
    auto cols = img_in.shape(1);
    auto type = CV_8UC3;

    cv::Mat img(rows, cols, type, (unsigned char*)img_in.data());

    // Create return vector
    vector<FaceBox> face_boxes;

    // Load face finder
    CascadeClassifier facecasc;
    facecasc.load("haarcascade_frontalface_default.xml");

    // Make sure we were able to load successfully.
    // If not, return empty vector
    if (facecasc.empty()) {
//        cerr << "XML file not loaded" << endl;
        return face_boxes;
    }
    else {
        vector<Rect> faces;
        struct FaceBox face;

        facecasc.detectMultiScale(img, faces, 1.05, 10);
        cout << "Faces vector size: " << faces.size() << endl;

        for (int i = 0; i < faces.size(); i++) {
//            cout << "Found face at: " << faces[i].tl();
            face.top_x = faces[i].tl().x;
            face.top_y = faces[i].tl().y;
            face.bottom_x = faces[i].br().x;
            face.bottom_y = faces[i].br().y;
            // Add face to vector
            face_boxes.push_back(face);
        }
    }

    return face_boxes;

}

//vector<FaceBox> get_largest_face(Mat img) {
//
//    // TODO - implement this function
//    // call get_face_locations
//    // loop through found faces
//    // find the largest face
//    // return it in a vector object of size(1)
//
//}

PYBIND11_MODULE(findfaces, m) {

    m.doc() = "OpenCV find faces binding";

    // Declare our FaceBox type
    // TODO - we could implement setters/getters here if wanted
    py::class_<FaceBox>(m, "FaceBox")
        .def_readwrite("top_x", &FaceBox::top_x)
        .def_readwrite("top_y", &FaceBox::top_y)
        .def_readwrite("bottom_x", &FaceBox::bottom_x)
        .def_readwrite("bottom_y", &FaceBox::bottom_y);

    // Declare our functions
    m.def("get_face_locations", &get_face_locations, "A function to find and return faces.");

}
