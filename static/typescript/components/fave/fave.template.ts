interface FaveTemplate {
  rootFragment: DocumentFragment;
  root: HTMLDivElement;
}

interface Context {}

export default function fave(
  context: Context,
  rootFragment: DocumentFragment = document.createDocumentFragment()
): FaveTemplate {
  const C = document.createElement("div");
  rootFragment.appendChild(C);
  const result: FaveTemplate = { rootFragment, root: C };
  return result;
}
