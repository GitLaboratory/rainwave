export interface RatingTemplate {
  rootFragment: HTMLElement | DocumentFragment;
  root: HTMLDivElement;
}

interface Context {}

export default function rating(
  context: Context,
  rootFragment:
    | HTMLElement
    | DocumentFragment = document.createDocumentFragment()
): RatingTemplate {
  let C: HTMLDivElement;
  C = document.createElement("div");
  rootFragment.appendChild(C);
  const result: RatingTemplate = { rootFragment, root: C };
  return result;
}
