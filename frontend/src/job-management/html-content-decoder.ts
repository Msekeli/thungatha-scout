export function decodeGreenhouseContent(value: string): string {
  const decoder = document.createElement("textarea");
  let decoded = value;

  for (let pass = 0; pass < 2; pass += 1) {
    decoder.innerHTML = decoded;
    if (decoder.value === decoded) break;
    decoded = decoder.value;
  }

  return decoded;
}
