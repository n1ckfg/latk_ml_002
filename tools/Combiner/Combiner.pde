PShape svg;
PShape latk;
PImage rgb, depth;
color[] svgColors;
float maxDist = 63;

void setup() {
  size(960, 720, P3D);
  setupCam(400);
  
  svg = loadShape("frame_00000-outputs.png.tga.svg");
  latk = createShape(GROUP);
  
  rgb = loadImage("frame_00000-targets.png");
  rgb.loadPixels();
  depth = loadImage("frame_00000-outputs.png");
  depth.loadPixels();
 
  for (int i=0; i<svg.getChildCount(); i++) {
    PShape child = svg.getChild(i);
    PShape newChild = createShape();
    
    int vertCount = child.getVertexCount();
    PVector p = new PVector(0,0,0);
    PVector pp = new PVector(0,0,0);
    
    for (int j=0; j<vertCount; j++) {
      PVector v = child.getVertex(j);
      int loc = int(v.x) + int(v.y) * (rgb.width-1);
      if (j==0) {
        color c = rgb.pixels[loc];
        newChild.setStroke(c);
        newChild.setFill(false);
        newChild.beginShape();
      }
      
      float z = red(depth.pixels[loc]);
      pp = p.copy();
      p = new PVector(v.x, v.y, z);
      if (j > 0) {
        if (PVector.dist(p, pp) > maxDist) break;
      }
      newChild.vertex(p.x, p.y, p.z);
      if (j >= vertCount-1) newChild.endShape();
    }
    
    latk.addChild(newChild);
  }
 
}

void draw() {
  background(127, 127, 150);
  
  shape(latk);
}
