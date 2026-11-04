export function decodeGreenhouseContent(value: string): string {
  const decoder = document.createElement("textarea");
  decoder.innerHTML = value;
  return decoder.value;
}
