import "server-only";

import { notFound } from "next/navigation";
import createClient from "openapi-fetch";

import type { components, paths } from "@/types/generated/assetgen";

export type Organization = components["schemas"]["Organization"];
export type Project = components["schemas"]["Project"];
export type Asset = components["schemas"]["Asset"];
export type Generation = components["schemas"]["Generation"];
export type Variant = components["schemas"]["Variant"];

const RAW_BASE =
    process.env.ASSETGEN_API_BASE_URL ??
    process.env.NEXT_PUBLIC_ASSETGEN_API_BASE_URL ??
    "";
const API_BASE = RAW_BASE.replace(/\/$/, "");

const BASE_URL = API_BASE || "";

const client = createClient<paths>({
    baseUrl: BASE_URL,
});

export class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

type ClientResponse<T> = {
    data: T | undefined;
    error?: unknown;
    response: Response;
};

function extractErrorMessage(error: unknown): string {
    if (!error) return "Unexpected API error";
    if (typeof error === "string") return error;
    if (
        typeof error === "object" &&
        error !== null &&
        "detail" in error &&
        typeof (error as { detail?: unknown }).detail === "string"
    ) {
        return (error as { detail?: string }).detail ?? "Unexpected API error";
    }
    try {
        return JSON.stringify(error);
    } catch {
        return "Unexpected API error";
    }
}

async function handleResponse<T>(
    promise: Promise<ClientResponse<T>>,
    {
        allowUndefined = false,
        notFoundOn404 = false,
    }: { allowUndefined?: boolean; notFoundOn404?: boolean } = {},
): Promise<T> {
    const { data, error, response } = await promise;

    if (error) {
        if (response.status === 404 && notFoundOn404) {
            notFound();
        }
        throw new ApiError(extractErrorMessage(error), response.status);
    }

    if (!allowUndefined && typeof data === "undefined") {
        throw new ApiError(
            "Unexpected empty response from API.",
            response.status,
        );
    }

    return data as T;
}

export async function listOrganizations(): Promise<Organization[]> {
    return handleResponse(
        client.GET("/api/orgs", { fetch: { cache: "no-store" } }),
    );
}

export async function getOrganization(orgId: string): Promise<Organization> {
    return handleResponse(
        client.GET("/api/orgs/{org_id}", {
            params: { path: { org_id: orgId } },
            fetch: { cache: "no-store" },
        }),
        { notFoundOn404: true },
    );
}

export async function listProjects(orgId: string): Promise<Project[]> {
    return handleResponse(
        client.GET("/api/orgs/{org_id}/projects", {
            params: { path: { org_id: orgId } },
            fetch: { cache: "no-store" },
        }),
    );
}

export async function getProject(
    orgId: string,
    projectId: string,
): Promise<Project> {
    return handleResponse(
        client.GET("/api/orgs/{org_id}/projects/{project_id}", {
            params: { path: { org_id: orgId, project_id: projectId } },
            fetch: { cache: "no-store" },
        }),
        { notFoundOn404: true },
    );
}

export async function listAssets(
    orgId: string,
    projectId: string,
): Promise<Asset[]> {
    return handleResponse(
        client.GET("/api/orgs/{org_id}/projects/{project_id}/assets", {
            params: { path: { org_id: orgId, project_id: projectId } },
            fetch: { cache: "no-store" },
        }),
    );
}

export async function getAsset(
    orgId: string,
    projectId: string,
    assetId: string,
): Promise<Asset> {
    return handleResponse(
        client.GET(
            "/api/orgs/{org_id}/projects/{project_id}/assets/{asset_id}",
            {
                params: {
                    path: {
                        org_id: orgId,
                        project_id: projectId,
                        asset_id: assetId,
                    },
                },
                fetch: { cache: "no-store" },
            },
        ),
        { notFoundOn404: true },
    );
}

export async function listGenerations(
    orgId: string,
    projectId: string,
    assetId: string,
): Promise<Generation[]> {
    return handleResponse(
        client.GET(
            "/api/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations",
            {
                params: {
                    path: {
                        org_id: orgId,
                        project_id: projectId,
                        asset_id: assetId,
                    },
                },
                fetch: { cache: "no-store" },
            },
        ),
    );
}

export async function listVariants(
    orgId: string,
    projectId: string,
    assetId: string,
    generationId: string,
): Promise<Variant[]> {
    return handleResponse(
        client.GET(
            "/api/orgs/{org_id}/projects/{project_id}/assets/{asset_id}/generations/{generation_id}/variants",
            {
                params: {
                    path: {
                        org_id: orgId,
                        project_id: projectId,
                        asset_id: assetId,
                        generation_id: generationId,
                    },
                },
                fetch: { cache: "no-store" },
            },
        ),
    );
}
