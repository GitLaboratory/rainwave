export interface FaveTemplate {
  rootFragment: HTMLElement | DocumentFragment;
  root: HTMLDivElement;
}

interface Context {}

export default function fave(
  context: Context,
  rootFragment:
    | HTMLElement
    | DocumentFragment = document.createDocumentFragment()
): FaveTemplate {
  let C: HTMLDivElement;
  C = document.createElement("div");
  rootFragment.appendChild(C);
  const result: FaveTemplate = { rootFragment, root: C };
  return result;
}
