  --api-key YOUR_OPENAI_API_KEY \
  --system-prompt system-prompt.txt \
  --user-prompt my-story.txt

# Choose Your Own Adventure World

An AI-powered, accessible, and proofread interactive story site for GitHub Pages.

---

## 🚀 Main Workflow

1. **Write your story prompt**  
   - Copy and edit `generator/story-prompt-template.txt` to create your own prompt file.

2. **Generate a story**  
   ```bash
   cd generator
   python generate_story.py --api-key YOUR_OPENAI_API_KEY --system-prompt system-prompt.txt --user-prompt my-story.txt
   ```
   - The generator will create a new story folder in `stories/` (but will NOT publish it yet).

3. **Proofread and publish**  
   - When generation finishes, you’ll be prompted:  
     “Run proofreading now? [Y/n]”
   - If you say yes, the proofreader will walk you through every node.
   - Accept all nodes to publish the story to `stories/index.json` (making it live on the site).
   - You can also run the proofreader later:
     ```bash
     python proofread_story.py
     ```
     - See a list of unpublished stories, pick one to proofread, or quit.

4. **Push to GitHub**  
   ```bash
   git add .
   git commit -m "Add new story"
   git push
   ```
   - Your new story will appear on the site after the push.

---

## 📝 Features

- **Proofreading required**: No story is published until every node is manually approved.
- **Favorites**: Users can favorite stories (local, no login needed).
- **Accessibility**:  
  - Dyslexia-friendly font  
  - High contrast mode  
  - Reduced motion  
  - Adjustable font size  
  - Keyboard navigation and ARIA labels
- **Category filtering**: Stories are tagged and filterable by genre.
- **Dynamic, static site**: No backend required; works on GitHub Pages.
- **AI generation**: Uses OpenAI GPT-4o-mini and DALL-E 3 for text and images.

---

## 🗂️ Project Structure

```
stories/
  index.json           # Published stories
  [story-id]/
    story.json         # Story structure
    nodes/*.txt        # Node text
    images/*.jpg       # Node images (optional)
generator/
  generate_story.py    # Story generator
  proofread_story.py   # Proofreading tool
assets/
  css/style.css
  js/
    index.js
    story-reader.js
    favorites.js
    accessibility.js
index.html             # Story list
reader.html            # Story reader
```

---

## 🧑‍💻 Usual Author Workflow

1. Edit your prompt (from template)
2. Run the generator
3. Proofread immediately (or later, via `python proofread_story.py`)
4. Accept all nodes to publish
5. Push to GitHub

---

## 🦾 User Features

- Browse, filter, and read stories
- Mark favorites (❤️)
- Use accessibility settings (⚙️ in header)
- Keyboard and screen reader friendly

---

## 🛠️ Local Development

```bash
python -m http.server 8000
# or use npx serve, php -S, etc.
```
Visit [http://localhost:8000](http://localhost:8000)

---

## 📚 More

- See `generator/PROOFREADING_README.md` for detailed proofreading instructions.
- See `FAVORITES_README.md` and `ACCESSIBILITY_README.md` for more on those features.

---

**Questions?**  
Just run `python proofread_story.py` for a list of unpublished stories and interactive help!
