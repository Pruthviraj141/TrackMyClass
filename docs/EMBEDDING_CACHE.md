# Embedding Cache Lifecycle

## Architecture

The `StudentEmbeddingCache` is an in-memory service mapping student identities to their face embeddings for real-time comparison.

## Lifecycle Methods

1. **Initialization**: The cache boots in an unloaded state.
2. **Loading (`load(institution_id)`)**: 
   - Retrieves all students for the target institution.
   - Extracts their stored JSON/Base64 embedding vectors.
   - Flattens them into a synchronized NumPy matrix (`self.embedding_matrix` size: `[N, 512]`).
   - Normalizes the matrix along the row axis (`||x|| = 1`) to enable cosine similarity matching via matrix multiplication.
3. **Refresh (`refresh(institution_id)`)**:
   - Drops the existing internal state.
   - Repeats the `load` sequence. This is typically invoked dynamically by the `RegistrationService` after a new student registers or deletes an account.
4. **Invalidation (`delete_identity(student_id)`)**:
   - For simple structural maintenance, specific entries can be removed without reloading all `N` vectors from the database.

## Session-State Isolation

To avoid leaking bounds across sessions belonging to different institutions:
- The `RecognitionEngine` strictly instantiates or loads the cache scoped by `institution_id`.
- The cache's memory matrix is completely bound to exactly the vectors associated with the parent institution. No candidate identities from Institution A can be returned while evaluating for Institution B.
