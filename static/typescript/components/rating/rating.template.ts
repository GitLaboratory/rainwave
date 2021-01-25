interface RatingTemplate {
  rootFragment: DocumentFragment;
  root: HTMLDivElement;
}

interface Context {}

export default function rating(
  context: Context,
  rootFragment: DocumentFragment = document.createDocumentFragment()
): RatingTemplate {
  const C = document.createElement("div");
  rootFragment.appendChild(C);
  const result: RatingTemplate = { rootFragment, root: C };
  return result;
}
