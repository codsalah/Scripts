import argparse
import os
import re
import sys
import tempfile
import threading
import wave


# ── Config ────────────────────────────────────────────────────────────────────
MIN_CHUNK   = 800
MAX_CHUNK   = 3000
MAX_THREADS = os.cpu_count()
MODEL_ID    = "KittenML/kitten-tts-mini-0.8"
# ─────────────────────────────────────────────────────────────────────────────


def split_text(text):
    """Split text into chunks sized dynamically based on text length."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    ideal_chunks = min(MAX_THREADS, max(1, len(text) // MIN_CHUNK))
    ideal_size   = max(MIN_CHUNK, min(MAX_CHUNK, len(text) // ideal_chunks))

    chunks, buffer = [], ""
    for sentence in sentences:
        buffer = (buffer + " " + sentence).strip() if buffer else sentence
        if len(buffer) >= ideal_size:
            chunks.append(buffer)
            buffer = ""
    if buffer:
        if chunks:
            chunks[-1] += " " + buffer
        else:
            chunks.append(buffer)

    return chunks


def clean(text):
    """Remove all newlines, tabs, and extra spaces."""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def generate_chunk(text, output_path, voice, speed, index, results, errors):
    try:
        from kittentts import KittenTTS
        # Each thread gets its own model instance — KittenTTS is not thread-safe
        m = KittenTTS(MODEL_ID)
        text = clean(text)
        print(f"  [Chunk {index+1}] {len(text)} chars...")
        m.generate_to_file(text, output_path, voice=voice, speed=speed)
        results[index] = output_path
        print(f"  [Chunk {index+1}] Done.")
    except Exception as e:
        errors[index] = str(e)
        print(f"  [Chunk {index+1}] Error: {e}")


def merge_wav(input_paths, output_path):
    with wave.open(input_paths[0], 'rb') as first:
        params = first.getparams()
    with wave.open(output_path, 'wb') as out:
        out.setparams(params)
        for path in input_paths:
            with wave.open(path, 'rb') as w:
                out.writeframes(w.readframes(w.getnframes()))


def process(input_path, output_path, voice, speed):
    with open(input_path, "r", encoding="utf-8") as f:
        content = clean(f.read())

    if not content:
        print(f"Error: File is empty: {input_path}")
        sys.exit(1)

    print(f"Input   : {input_path}")
    print(f"Output  : {output_path}")
    print(f"Voice   : {voice}")
    print(f"Speed   : {speed}")
    print(f"Length  : {len(content)} characters")
    print(f"Cores   : {MAX_THREADS}")

    chunks = split_text(content)
    print(f"Chunks  : {len(chunks)} (sizes: {[len(c) for c in chunks]})\n")

    tmp_dir   = tempfile.mkdtemp()
    tmp_paths = [os.path.join(tmp_dir, f"chunk_{i}.wav") for i in range(len(chunks))]
    results   = [None] * len(chunks)
    errors    = [None] * len(chunks)

    threads = [
        threading.Thread(
            target=generate_chunk,
            args=(chunk, tmp_path, voice, speed, i, results, errors)
        )
        for i, (chunk, tmp_path) in enumerate(zip(chunks, tmp_paths))
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    failed = [i for i, e in enumerate(errors) if e is not None]
    if failed:
        print(f"\nFailed chunks: {[i+1 for i in failed]}")
        for i in failed:
            print(f"  Chunk {i+1}: {errors[i]}")
        sys.exit(1)

    merge_wav(results, output_path)

    for p in tmp_paths:
        if os.path.exists(p): os.remove(p)
    os.rmdir(tmp_dir)

    print(f"\nDone! Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        prog='kittenreader',
        description='Generate speech from a text file using KittenTTS (multithreaded)',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""voices:
  Female: Bella, Luna, Rosie, Kiki
    Luna  = Strict nerd
    Kiki  = Childish
    Bella = Neutral steady
    Rosie = Podcast soft
  Male:   Jasper, Bruno, Hugo, Leo

examples:
  kittenreader input.txt
  kittenreader input.txt output.wav
  kittenreader input.txt --voice Rosie --speed 1.25
  kittenreader input.txt /tmp/result.wav --voice Luna --speed 1.0
        """
    )

    parser.add_argument('input',  help='Path to the input .txt file')
    parser.add_argument('output', nargs='?', default=None,
                        help='Path for the output .wav file (default: same name as input)')
    parser.add_argument('--voice', default='Rosie',
                        choices=['Bella', 'Luna', 'Rosie', 'Kiki', 'Jasper', 'Bruno', 'Hugo', 'Leo'],
                        help='Voice to use (default: Rosie)')
    parser.add_argument('--speed', type=float, default=1.0,
                        help='Speech speed multiplier (default: 1.0)')

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.isfile(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_path = os.path.abspath(args.output) if args.output else \
                  os.path.splitext(input_path)[0] + ".wav"

    try:
        from kittentts import KittenTTS  # noqa: just checking it's installed
    except ImportError:
        print("Error: KittenTTS is not installed.")
        print("Install: pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl")
        sys.exit(1)

    process(input_path, output_path, args.voice, args.speed)


if __name__ == '__main__':
    main()