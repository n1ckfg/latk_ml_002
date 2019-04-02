PShape svg;
PShape latk;
PImage rgb, depth;
color[] svgColors;
float maxDist = 50;
float minDepth = 0.1;

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
    color c = color(0);
    for (int j=0; j<vertCount; j++) {
      PVector v = child.getVertex(j);
      int loc = int(v.x) + int(v.y) * (rgb.width-1);
      if (j==0) {
        c = rgb.pixels[loc];
        newChild.setFill(false);
        newChild.beginShape();
      }
      
      float z = red(depth.pixels[loc]);
      if (z > minDepth) {
        pp = p.copy();
        p = new PVector(v.x, v.y, z);
        if (j > 0) {
          if (PVector.dist(p, pp) > maxDist) break;
        }
        newChild.stroke(c);
        newChild.vertex(p.x, p.y, p.z);
        if (j >= vertCount-1) newChild.endShape();
      }
    }
    
    latk.addChild(newChild);
  }
 
   for (int i=0; i<svg.getChildCount(); i++) {
    PShape child = svg.getChild(i);
    color c = color(random(127) + 127, random(127) + 127, random(127) + 127);
    child.setStroke(c);
  }
}

void draw() {
  background(127, 127, 150);
  shape(svg);

   for (int i=0; i<svg.getChildCount(); i++) {
    PShape child = svg.getChild(i);
    for (int j=0; j<child.getVertexCount(); j++) {
      PVector v = child.getVertex(j);
      stroke(0);
      strokeWeight(2);
      point(v.x, v.y);
    }
  }
  
  surface.setTitle("" + frameRate);
}
