#include <gflags/gflags.h>

DEFINE_string(i, "", "input file path");
DEFINE_string(o, "", "output file path");
DEFINE_double(dt, 1.5, "line fitting distance threshold");
DEFINE_int32(lt, 20, "line length threshold");
DEFINE_bool(show, true, "show the labeled result in a window");

#include "linedetector.h"

// gflags 2.1 moved the library out of the "google" namespace. gflags_declare.h
// defines GFLAGS_NAMESPACE for whichever one this install was built with.
#ifndef GFLAGS_NAMESPACE
#define GFLAGS_NAMESPACE google
#endif

/** Main function*/
int main(int argc, char* argv[]) {
  GFLAGS_NAMESPACE::ParseCommandLineFlags(&argc, &argv, true);
  if(FLAGS_i=="") {
    fprintf(stderr, "Define input file path.\n");
    cout << "Usage: " << argv[0] << " -i /input/file/path.png (optional)-o /output/file/path.txt (optional)-dt distance_threshold (optional)-lt length_threshold" << endl;
    return 1;
  }

  LineDetector ld;
  vector<SEGMENT> lines;
  Mat src = imread(FLAGS_i, IMREAD_COLOR);
  if(src.empty()) {
    fprintf(stderr,"cannot open the input file!\n");
    return 1;
  }

  Mat src_gray;
  cvtColor(src, src_gray, COLOR_BGR2GRAY);
  lines.clear();
  ld.lineDetection(src_gray, lines);

  FILE *fptr;
  string outfile;
  if(FLAGS_o=="") {
    outfile=FLAGS_i+"_lines.txt";
  }
  else {
    outfile=FLAGS_o;
  }
  cout << "Writing coordinates of lines to file " << outfile << endl;
  fptr = fopen(outfile.c_str(), "w");
  if(fptr==NULL) {
    fprintf(stderr, "cannot write to %s\n", outfile.c_str());
    return 1;
  }
  for (size_t i=0; i<lines.size(); i++) {
    SEGMENT seg=lines.at(i);
    fprintf(fptr, "%d %.5f %.5f %.5f %.5f %.5f \n",seg.label,seg.angle,seg.x1,seg.y1,seg.x2,seg.y2);
  }
  fclose(fptr);

  Mat blank = Mat::ones(src.rows, src.cols, CV_8UC1);
  blank += 255;
  Mat blank_color;
  cvtColor(blank, blank_color, COLOR_GRAY2BGR);

  for(size_t i=0; i<lines.size(); i++) {
    SEGMENT seg=lines.at(i);

    int b = (seg.label*12337) % 256;
    int g = (seg.label*24776) % 256;
    int r = (seg.label*11491) % 256;

    ld.drawArrow(src, &seg, Scalar(b,g,r));
    char cLabel[64];
    snprintf(cLabel,sizeof(cLabel),"%d",seg.label);
    Point2i pM;
    pM.x = (seg.x1+seg.x2)/2;
    pM.y = (seg.y1+seg.y2)/2;
    Point2i pe1;
    double dGap = 15.0;
    if(seg.angle < CV_PI / 1.5f) dGap = 5.0;
    double dAngle = (double)seg.angle;
    double dArrowAng = 89.0;
    pe1.x = cvRound(pM.x - dGap*cos(dArrowAng * CV_PI / 180.0 + dAngle));
    pe1.y = cvRound(pM.y - dGap*sin(dArrowAng * CV_PI / 180.0 + dAngle));
    putText(src, cLabel, pe1, FONT_HERSHEY_PLAIN, 1, Scalar(b,g,r), 1, 8, false);
    line(blank_color, Point2f(seg.x1, seg.y1), Point2f(seg.x2, seg.y2), Scalar(0,0,255));
  }

  string outimgpath=FLAGS_i+"_labeled.png";
  imwrite(outimgpath, src);
  cout << outimgpath << " saved. " << endl;
  outimgpath=FLAGS_i+"_only_lines.png";
  imwrite(outimgpath, blank_color);
  cout << outimgpath << " saved. " << endl;
  cout << "lines.size() = " << lines.size() << endl;

  // Drawn last so the results are written out even where there is no display.
  if(FLAGS_show) {
    try {
      imshow(FLAGS_i, src);
      waitKey(0);
    } catch(const cv::Exception & e) {
      cout << "no display available, skipping the preview window." << endl;
    }
  }

  return 0;
}
