"""
Firebase Firestore accessor helper for the AssetGen API.

This module provides a lightweight wrapper around google-cloud-firestore to:
- initialize a Firestore client (optionally from a service account JSON)
- provide convenience CRUD helpers for the hierarchical multi-tenant schema:
  organizations/{orgId}/projects/{projectId}/assets/{assetId}/generations/{genId}/variants/{variantId}
- convert between Pydantic models (in `api.models`) and Firestore documents
- optionally set Firestore server timestamps on create/update

Usage
-----
from .firebase import FirestoreAccessor
from .models import Organization

acc = FirestoreAccessor()
org = Organization(name="ACME Org", owner_user_id="user_123")
created = acc.create_organization(org, org_id="org_123")

Notes
-----
- This file expects the `google-cloud-firestore` package to be installed.
- Authentication is managed by the standard GOOGLE_APPLICATION_CREDENTIALS env var,
  or by passing `credentials_path` to the accessor.
- For emulator usage, set the FIRESTORE_EMULATOR_HOST environment variable before
  initializing the accessor (or pass use_emulator=True).
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar

try:
    from google.cloud import firestore
    from google.oauth2 import service_account
except (
    Exception
) as e:  # pragma: no cover - imports may fail in environments without the client lib
    firestore = None  # type: ignore
    service_account = None  # type: ignore

from pydantic import BaseModel

# Import models from local package
from .models import (
    Asset,
    AssetWithGenerations,
    ConceptImage,
    Generation,
    GenerationWithVariants,
    Organization,
    Project,
    User,
    Variant,
    Theme,
    StyleGuide,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


T = TypeVar("T", bound=BaseModel)


class FirestoreError(RuntimeError):
    """Generic Firestore wrapper error."""


class FirestoreAccessor:
    """
    Firestore accessor for the AssetGen tool.

    Example paths used:
      - organizations/{org_id}
      - organizations/{org_id}/projects/{project_id}
      - organizations/{org_id}/projects/{project_id}/assets/{asset_id}
      - organizations/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{gen_id}
      - .../variants/{variant_id}
      - organizations/{org_id}/projects/{project_id}/conceptImages/{image_id}
      - organizations/{org_id}/projects/{project_id}/themes/{theme_id}

    Initialization:
      FirestoreAccessor(project=None, credentials_path=None, use_emulator=False)
    """

    def __init__(
        self,
        project: Optional[str] = None,
        credentials_path: Optional[str] = None,
        use_emulator: bool = False,
    ) -> None:
        if firestore is None:
            raise FirestoreError(
                "google-cloud-firestore is required but not installed in this environment."
            )

        # If emulator requested, the environment variable must be set (client honors it)
        if use_emulator:
            # If FIRESTORE_EMULATOR_HOST isn't set, we log a warning but continue; client will error if misconfigured
            if "FIRESTORE_EMULATOR_HOST" not in os.environ:
                logger.warning(
                    "use_emulator=True but FIRESTORE_EMULATOR_HOST not set in environment."
                )

        # Load credentials if provided:
        credentials = None
        if credentials_path:
            if service_account is None:
                raise FirestoreError(
                    "google.oauth2.service_account is required to load credentials from a file."
                )
            if not os.path.exists(credentials_path):
                raise FirestoreError(f"Credentials file not found: {credentials_path}")
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )

        # Create client
        try:
            if credentials:
                self.client = firestore.Client(project=project, credentials=credentials)
            else:
                # Client will auto-detect credentials from environment or metadata server
                self.client = firestore.Client(project=project)
        except Exception as ex:
            raise FirestoreError(f"Failed to initialize Firestore client: {ex}") from ex

        # Shortcuts for top-level collections
        self.orgs_col = self.client.collection("organizations")

    # -------------------------
    # Helper utilities
    # -------------------------
    @staticmethod
    def _model_to_dict(model: BaseModel, include_id: bool = False) -> Dict[str, Any]:
        """
        Convert a Pydantic model to a Firestore-friendly dict.
        By default excludes None fields.
        If include_id is True, include the `id` attribute if present.
        """
        data = model.dict(exclude_none=True)
        if not include_id and "id" in data:
            data.pop("id")
        return data

    @staticmethod
    def _apply_server_timestamps(
        d: Dict[str, Any], timestamp_fields: Iterable[str]
    ) -> Dict[str, Any]:
        """
        Replace keys in timestamp_fields with Firestore SERVER_TIMESTAMP sentinel.
        """
        for k in timestamp_fields:
            d[k] = firestore.SERVER_TIMESTAMP
        return d

    @staticmethod
    def _doc_to_model(
        doc_snapshot: firestore.DocumentSnapshot, model_cls: Type[T]
    ) -> Optional[T]:
        """
        Convert a DocumentSnapshot to a Pydantic model instance.
        Returns None if the snapshot does not exist.
        """
        if not doc_snapshot.exists:
            return None
        data = doc_snapshot.to_dict()
        # Attach id into data so model can see it
        data["id"] = doc_snapshot.id
        try:
            return model_cls(**data)
        except Exception as ex:
            # If construction fails, raise a helpful error
            raise FirestoreError(
                f"Failed to parse document {doc_snapshot.id} into {model_cls}: {ex}"
            ) from ex

    @staticmethod
    def _attach_metadata(model: T, **fields: Any) -> T:
        """
        Attach contextual metadata (like org_id/project_id) to a Pydantic model instance
        if the model defines those attributes.
        """
        for key, value in fields.items():
            if value is not None and hasattr(model, key):
                setattr(model, key, value)
        return model

    @staticmethod
    def _query_to_models(
        query_snapshot: Iterable[firestore.DocumentSnapshot], model_cls: Type[T]
    ) -> List[T]:
        """
        Convert an iterable of DocumentSnapshot to a list of Pydantic models (skips non-existing).
        """
        results: List[T] = []
        for doc in query_snapshot:
            model = FirestoreAccessor._doc_to_model(doc, model_cls)
            if model:
                results.append(model)
        return results

    # -------------------------
    # Generic document helpers
    # -------------------------
    def _create_doc(
        self,
        collection_ref: firestore.CollectionReference,
        data: Dict[str, Any],
        doc_id: Optional[str] = None,
        set_timestamps: bool = True,
    ) -> firestore.DocumentReference:
        """
        Create a document in `collection_ref`. If doc_id is provided, use it, otherwise let Firestore auto-generate.
        If set_timestamps is True, set both created_at and updated_at to server timestamps if those keys exist in data or are desired.
        Returns the DocumentReference of the created doc.
        """
        payload = dict(data)  # shallow copy
        if set_timestamps:
            # prefer to set created_at/updated_at to server timestamp if not provided
            if "created_at" not in payload:
                payload["created_at"] = firestore.SERVER_TIMESTAMP
            payload["updated_at"] = firestore.SERVER_TIMESTAMP

        try:
            if doc_id:
                doc_ref = collection_ref.document(doc_id)
                doc_ref.set(payload)
            else:
                doc_ref = collection_ref.add(payload)[
                    1
                ]  # returns (write_result, doc_ref)
        except Exception as ex:
            raise FirestoreError(
                f"Error creating document in {collection_ref.path}: {ex}"
            ) from ex

        return doc_ref

    def _get_doc(
        self, doc_ref: firestore.DocumentReference, model_cls: Type[T]
    ) -> Optional[T]:
        try:
            snapshot = doc_ref.get()
        except Exception as ex:
            raise FirestoreError(f"Error reading document {doc_ref.path}: {ex}") from ex

        return self._doc_to_model(snapshot, model_cls)

    def _update_doc(
        self,
        doc_ref: firestore.DocumentReference,
        updates: Dict[str, Any],
        set_updated_at: bool = True,
    ) -> None:
        payload = dict(updates)
        if set_updated_at:
            payload["updated_at"] = firestore.SERVER_TIMESTAMP
        try:
            doc_ref.update(payload)
        except Exception as ex:
            raise FirestoreError(
                f"Error updating document {doc_ref.path}: {ex}"
            ) from ex

    def _delete_doc(self, doc_ref: firestore.DocumentReference) -> None:
        try:
            doc_ref.delete()
        except Exception as ex:
            raise FirestoreError(
                f"Error deleting document {doc_ref.path}: {ex}"
            ) from ex

    # -------------------------
    # Organization helpers
    # -------------------------
    def create_organization(
        self, org: Organization, org_id: Optional[str] = None
    ) -> Organization:
        """
        Create an Organization document under organizations/{orgId}.
        If org_id is provided, it will be used as the document ID; otherwise Firestore generates one.
        Returns the created Organization model (including assigned id).
        """
        data = self._model_to_dict(org, include_id=False)
        col = self.orgs_col
        doc_ref = self._create_doc(col, data, doc_id=org_id)
        created = self._get_doc(doc_ref, Organization)
        if created is None:
            raise FirestoreError("Failed to read back created organization.")
        return created

    def get_organization(self, org_id: str) -> Optional[Organization]:
        doc_ref = self.orgs_col.document(org_id)
        return self._get_doc(doc_ref, Organization)

    def list_organizations(self) -> List[Organization]:
        try:
            snaps = self.orgs_col.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing organizations: {ex}") from ex
        return self._query_to_models(snaps, Organization)

    def update_organization(self, org_id: str, updates: Dict[str, Any]) -> None:
        doc_ref = self.orgs_col.document(org_id)
        self._update_doc(doc_ref, updates)

    def delete_organization(self, org_id: str) -> None:
        # Note: This does not recursively delete subcollections
        doc_ref = self.orgs_col.document(org_id)
        self._delete_doc(doc_ref)

    # -------------------------
    # Project helpers
    # -------------------------
    def _projects_col(self, org_id: str) -> firestore.CollectionReference:
        return self.orgs_col.document(org_id).collection("projects")

    def create_project(
        self, org_id: str, project: Project, project_id: Optional[str] = None
    ) -> Project:
        data = self._model_to_dict(project, include_id=False)
        col = self._projects_col(org_id)
        doc_ref = self._create_doc(col, data, doc_id=project_id)
        created = self._get_doc(doc_ref, Project)
        if created is None:
            raise FirestoreError("Failed to read back created project.")
        return self._attach_metadata(created, org_id=org_id)

    def get_project(self, org_id: str, project_id: str) -> Optional[Project]:
        doc_ref = self._projects_col(org_id).document(project_id)
        project = self._get_doc(doc_ref, Project)
        if project:
            return self._attach_metadata(project, org_id=org_id)
        return None

    def list_projects(self, org_id: str) -> List[Project]:
        col = self._projects_col(org_id)
        try:
            snaps = col.get()
        except Exception as ex:
            raise FirestoreError(
                f"Error listing projects for org {org_id}: {ex}"
            ) from ex
        return [
            self._attach_metadata(project, org_id=org_id)
            for project in self._query_to_models(snaps, Project)
        ]

    def update_project(
        self, org_id: str, project_id: str, updates: Dict[str, Any]
    ) -> None:
        doc_ref = self._projects_col(org_id).document(project_id)
        self._update_doc(doc_ref, updates)

    # -------------------------
    # Asset helpers
    # -------------------------
    def _assets_col(
        self, org_id: str, project_id: str
    ) -> firestore.CollectionReference:
        return self._projects_col(org_id).document(project_id).collection("assets")

    def create_asset(
        self, org_id: str, project_id: str, asset: Asset, asset_id: Optional[str] = None
    ) -> Asset:
        data = self._model_to_dict(asset, include_id=False)
        col = self._assets_col(org_id, project_id)
        doc_ref = self._create_doc(col, data, doc_id=asset_id)
        created = self._get_doc(doc_ref, Asset)
        if created is None:
            raise FirestoreError("Failed to read back created asset.")
        return self._attach_metadata(created, org_id=org_id, project_id=project_id)

    def get_asset(self, org_id: str, project_id: str, asset_id: str) -> Optional[Asset]:
        doc_ref = self._assets_col(org_id, project_id).document(asset_id)
        asset = self._get_doc(doc_ref, Asset)
        if asset:
            return self._attach_metadata(asset, org_id=org_id, project_id=project_id)
        return None

    def list_assets(
        self, org_id: str, project_id: str, where: Optional[List[Any]] = None
    ) -> List[Asset]:
        """
        List assets under a project. Optional `where` can be a list of 3-tuples for filters:
          [('tags', 'array_contains', 'robot'), ('theme_id', '==', 'neo-noir')]
        """
        col = self._assets_col(org_id, project_id)
        q = col
        if where:
            for clause in where:
                if len(clause) != 3:
                    raise ValueError(
                        "Each where clause must be a 3-tuple: (field, op, value)"
                    )
                q = q.where(clause[0], clause[1], clause[2])
        try:
            snaps = q.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing assets: {ex}") from ex
        return [
            self._attach_metadata(asset, org_id=org_id, project_id=project_id)
            for asset in self._query_to_models(snaps, Asset)
        ]

    def update_asset(
        self, org_id: str, project_id: str, asset_id: str, updates: Dict[str, Any]
    ) -> None:
        doc_ref = self._assets_col(org_id, project_id).document(asset_id)
        self._update_doc(doc_ref, updates)

    def delete_asset(self, org_id: str, project_id: str, asset_id: str) -> None:
        doc_ref = self._assets_col(org_id, project_id).document(asset_id)
        self._delete_doc(doc_ref)

    # -------------------------
    # Generation helpers
    # -------------------------
    def _generations_col(
        self, org_id: str, project_id: str, asset_id: str
    ) -> firestore.CollectionReference:
        return (
            self._assets_col(org_id, project_id)
            .document(asset_id)
            .collection("generations")
        )

    def create_generation(
        self,
        org_id: str,
        project_id: str,
        asset_id: str,
        generation: Generation,
        generation_id: Optional[str] = None,
    ) -> Generation:
        data = self._model_to_dict(generation, include_id=False)
        col = self._generations_col(org_id, project_id, asset_id)
        doc_ref = self._create_doc(col, data, doc_id=generation_id)
        created = self._get_doc(doc_ref, Generation)
        if created is None:
            raise FirestoreError("Failed to read back created generation.")
        return self._attach_metadata(
            created,
            org_id=org_id,
            project_id=project_id,
            asset_id=asset_id,
        )

    def get_generation(
        self, org_id: str, project_id: str, asset_id: str, generation_id: str
    ) -> Optional[Generation]:
        doc_ref = self._generations_col(org_id, project_id, asset_id).document(
            generation_id
        )
        generation = self._get_doc(doc_ref, Generation)
        if generation:
            return self._attach_metadata(
                generation,
                org_id=org_id,
                project_id=project_id,
                asset_id=asset_id,
            )
        return None

    def list_generations(
        self,
        org_id: str,
        project_id: str,
        asset_id: str,
        order_by: str = "created_at",
        desc: bool = True,
    ) -> List[Generation]:
        col = self._generations_col(org_id, project_id, asset_id)
        q = col.order_by(
            order_by,
            direction=firestore.Query.DESCENDING if desc else firestore.Query.ASCENDING,
        )
        try:
            snaps = q.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing generations: {ex}") from ex
        return [
            self._attach_metadata(
                generation,
                org_id=org_id,
                project_id=project_id,
                asset_id=asset_id,
            )
            for generation in self._query_to_models(snaps, Generation)
        ]

    def update_generation(
        self,
        org_id: str,
        project_id: str,
        asset_id: str,
        generation_id: str,
        updates: Dict[str, Any],
    ) -> None:
        doc_ref = self._generations_col(org_id, project_id, asset_id).document(
            generation_id
        )
        self._update_doc(doc_ref, updates)

    # -------------------------
    # Variant helpers
    # -------------------------
    def _variants_col(
        self, org_id: str, project_id: str, asset_id: str, generation_id: str
    ) -> firestore.CollectionReference:
        return (
            self._generations_col(org_id, project_id, asset_id)
            .document(generation_id)
            .collection("variants")
        )

    def create_variant(
        self,
        org_id: str,
        project_id: str,
        asset_id: str,
        generation_id: str,
        variant: Variant,
        variant_id: Optional[str] = None,
    ) -> Variant:
        data = self._model_to_dict(variant, include_id=False)
        col = self._variants_col(org_id, project_id, asset_id, generation_id)
        doc_ref = self._create_doc(col, data, doc_id=variant_id)
        created = self._get_doc(doc_ref, Variant)
        if created is None:
            raise FirestoreError("Failed to read back created variant.")
        return self._attach_metadata(
            created,
            org_id=org_id,
            project_id=project_id,
            asset_id=asset_id,
            generation_id=generation_id,
        )

    def get_variant(
        self,
        org_id: str,
        project_id: str,
        asset_id: str,
        generation_id: str,
        variant_id: str,
    ) -> Optional[Variant]:
        doc_ref = self._variants_col(
            org_id, project_id, asset_id, generation_id
        ).document(variant_id)
        variant = self._get_doc(doc_ref, Variant)
        if variant:
            return self._attach_metadata(
                variant,
                org_id=org_id,
                project_id=project_id,
                asset_id=asset_id,
                generation_id=generation_id,
            )
        return None

    def list_variants(
        self, org_id: str, project_id: str, asset_id: str, generation_id: str
    ) -> List[Variant]:
        col = self._variants_col(org_id, project_id, asset_id, generation_id)
        try:
            snaps = col.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing variants: {ex}") from ex
        return [
            self._attach_metadata(
                variant,
                org_id=org_id,
                project_id=project_id,
                asset_id=asset_id,
                generation_id=generation_id,
            )
            for variant in self._query_to_models(snaps, Variant)
        ]

    # -------------------------
    # Theme helpers
    # -------------------------
    def _themes_col(
        self, org_id: str, project_id: str
    ) -> firestore.CollectionReference:
        return self._projects_col(org_id).document(project_id).collection("themes")

    def create_theme(
        self, org_id: str, project_id: str, theme: Theme, theme_id: Optional[str] = None
    ) -> Theme:
        data = self._model_to_dict(theme, include_id=False)
        col = self._themes_col(org_id, project_id)
        doc_ref = self._create_doc(col, data, doc_id=theme_id)
        created = self._get_doc(doc_ref, Theme)
        if created is None:
            raise FirestoreError("Failed to read back created theme.")
        return self._attach_metadata(created, org_id=org_id, project_id=project_id)

    def list_themes(self, org_id: str, project_id: str) -> List[Theme]:
        col = self._themes_col(org_id, project_id)
        try:
            snaps = col.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing themes: {ex}") from ex
        return [
            self._attach_metadata(theme, org_id=org_id, project_id=project_id)
            for theme in self._query_to_models(snaps, Theme)
        ]

    # -------------------------
    # ConceptImage helpers
    # -------------------------
    def _concept_images_col(
        self, org_id: str, project_id: str
    ) -> firestore.CollectionReference:
        return (
            self._projects_col(org_id).document(project_id).collection("conceptImages")
        )

    def create_concept_image(
        self,
        org_id: str,
        project_id: str,
        ci: ConceptImage,
        image_id: Optional[str] = None,
    ) -> ConceptImage:
        data = self._model_to_dict(ci, include_id=False)
        col = self._concept_images_col(org_id, project_id)
        doc_ref = self._create_doc(col, data, doc_id=image_id)
        created = self._get_doc(doc_ref, ConceptImage)
        if created is None:
            raise FirestoreError("Failed to read back created concept image.")
        return self._attach_metadata(created, org_id=org_id, project_id=project_id)

    def list_concept_images(
        self, org_id: str, project_id: str, tag: Optional[str] = None
    ) -> List[ConceptImage]:
        col = self._concept_images_col(org_id, project_id)
        q = col
        if tag:
            q = q.where("tags", "array_contains", tag)
        try:
            snaps = q.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing concept images: {ex}") from ex
        return [
            self._attach_metadata(ci, org_id=org_id, project_id=project_id)
            for ci in self._query_to_models(snaps, ConceptImage)
        ]

    # -------------------------
    # User helpers
    # -------------------------
    def _users_col(self) -> firestore.CollectionReference:
        return self.client.collection("users")

    def create_user(self, user: User, user_id: Optional[str] = None) -> User:
        data = self._model_to_dict(user, include_id=False)
        col = self._users_col()
        doc_ref = self._create_doc(col, data, doc_id=user_id)
        created = self._get_doc(doc_ref, User)
        if created is None:
            raise FirestoreError("Failed to read back created user.")
        return created

    def get_user(self, user_id: str) -> Optional[User]:
        doc_ref = self._users_col().document(user_id)
        return self._get_doc(doc_ref, User)

    def list_users(self) -> List[User]:
        col = self._users_col()
        try:
            snaps = col.get()
        except Exception as ex:
            raise FirestoreError(f"Error listing users: {ex}") from ex
        return self._query_to_models(snaps, User)

    # -------------------------
    # Convenience operations
    # -------------------------
    def create_asset_with_first_generation(
        self,
        org_id: str,
        project_id: str,
        asset: Asset,
        generation: Generation,
        asset_id: Optional[str] = None,
        generation_id: Optional[str] = None,
    ) -> AssetWithGenerations:
        """
        Create an asset and an initial generation in a single transaction.
        Returns AssetWithGenerations containing created asset and generation(s).
        """

        def transaction_fn(transaction):
            col = self._assets_col(org_id, project_id)
            if asset_id:
                asset_ref = col.document(asset_id)
                transaction.set(asset_ref, self._model_to_dict(asset, include_id=False))
            else:
                # mimic add in transaction by creating a new ID first
                asset_ref = col.document()
                transaction.set(asset_ref, self._model_to_dict(asset, include_id=False))

            gen_col = asset_ref.collection("generations")
            gen_ref = (
                gen_col.document(generation_id) if generation_id else gen_col.document()
            )
            transaction.set(gen_ref, self._model_to_dict(generation, include_id=False))
            return asset_ref.id, gen_ref.id

        try:
            asset_id_created, gen_id_created = self.client.transaction()(transaction_fn)
        except Exception as ex:
            raise FirestoreError(
                f"Transaction failed creating asset and generation: {ex}"
            ) from ex

        asset_model = self.get_asset(org_id, project_id, asset_id_created)
        gen_model = self.get_generation(
            org_id, project_id, asset_id_created, gen_id_created
        )
        if not asset_model or not gen_model:
            raise FirestoreError(
                "Failed to fetch created asset or generation after transaction."
            )

        return AssetWithGenerations(**asset_model.dict(), generations=[gen_model])

    # -------------------------
    # Utility: convert generation with variants snapshot into models
    # -------------------------
    def get_generation_with_variants(
        self, org_id: str, project_id: str, asset_id: str, generation_id: str
    ) -> Optional[GenerationWithVariants]:
        gen = self.get_generation(org_id, project_id, asset_id, generation_id)
        if not gen:
            return None
        variants = self.list_variants(org_id, project_id, asset_id, generation_id)
        # Build combined model
        data = gen.dict()
        data["variants"] = [v.dict() for v in variants]
        data["id"] = generation_id
        return GenerationWithVariants(**data)


# End of file
