#include <opencv2/opencv.hpp>

int main() {
    // IP address and port of the IP camera
    std::string ip_address = "http://username:password@ip_address:port/video";
    
    // Open the video stream from the IP camera
    cv::VideoCapture cap(ip_address);
    
    // Check if the video stream is opened successfully
    if (!cap.isOpened()) {
        std::cout << "Error: Could not open the video stream from the IP camera." << std::endl;
        return -1;
    }

    // Create a window to display the video feed
    cv::namedWindow("IP Camera Feed", cv::WINDOW_NORMAL);
    
    while (true) {
        cv::Mat frame;
        
        // Read a frame from the video stream
        cap >> frame;
        
        // Check if the frame is empty
        if (frame.empty()) {
            std::cout << "Error: Frame is empty." << std::endl;
            break;
        }
        
        // Display the frame in the window
        cv::imshow("IP Camera Feed", frame);
        
        // Break the loop if 'q' is pressed
        if (cv::waitKey(1) == 'q') {
            break;
        }
    }
    
    // Release the video capture object and destroy the window
    cap.release();
    cv::destroyAllWindows();
    
    return 0;
}
