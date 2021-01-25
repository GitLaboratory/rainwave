export function svg(icon: string): SVGSVGElement {
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  var use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttributeNS(
    "http://www.w3.org/1999/xlink",
    "xlink:href",
    "/static/images4/symbols.svg#" + icon
  );
  svg.appendChild(use);
  return svg;
}

