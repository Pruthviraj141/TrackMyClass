# AI Pipeline Audit

## 1. Stack and Preprocessing
The system uses the `facenet-pytorch` wrapper holding:
1. **MTCNN (Multi-task Cascaded Convolutional Networks)**: Handles multi-face spatial recognition and dynamic cropping (`MTCNN_IMAGE_SIZE = 160`).
2. **InceptionResnetV1**: Configured under pre-trained `vggface2` weights mapping images down to `512` feature vectors (`EMBEDDING_DIM = 512`).

### 2. Loading
Models are treated as Python singletons via `backend.services.face_detection` and `backend.models.facenet_model`. They are instantiated via FastAPI's `@asynccontextmanager lifespan()` on startup on the CPU (`DEVICE = 'cpu'`), which eliminates the massive multi-second startup latency per request, keeping subsequent requests fast.

### 3. Pipeline Flow (`mark-attendance`)
1. **Frontend**: Sends variable quality/size base64 JPEGs.
2. **Resize Optimization**: Python forces resolution down via `Image.resize((640, new_h))` maintaining aspect bounds.
3. **Detection**: `detect_faces()` passes image to MTCNN.
4. **Extraction**: Detected Tensors iteratively pushed via `generate_embedding()` yielding `512` features.
5. **Matching**: Numpy `@` (Dot-product matrix multiplication) triggers cosine-similarity over normalized caching (`optimized_recognition.py`) to bypass database I/O.
6. **Temporal Evaluation**: Confidences are aggregated by `temporal_tracker.py`. If 4 consecutive frames > 80% confidence, consider matched.

## Findings & Flaws
- **Linear processing**: The AI iterates over multiple cropped faces (`for i in range(len(face_tensors))`). It should utilize batch Tensor operations across FaceNet to handle high density frames simultaneously.
- No GPU invocation parameterizing available dynamically, relies on strict CPU binding unless code is altered.
- **Decoding overhead**: Converting base64 -> BytesIO -> PIL image per frame is exceptionally expensive CPU usage vs raw canvas byte buffers.
