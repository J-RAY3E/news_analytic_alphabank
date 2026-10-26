"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { dataApi } from "@/lib/mocks/api";
import type {
  FeedbackRequest,
  IngestRequest,
  InsightRequest,
  Role,
} from "./types";

export function useCompanies() {
  return useQuery({
    queryKey: ["companies"],
    queryFn: () => dataApi.listCompanies(),
    select: (d) => d.items,
  });
}

export function useFeed(companyId: string | null, role: Role, limit = 10) {
  return useQuery({
    queryKey: ["feed", companyId, role, limit],
    queryFn: () => dataApi.getFeed(companyId!, role, limit),
    enabled: Boolean(companyId),
  });
}

export function useEvent(eventId: string | null) {
  return useQuery({
    queryKey: ["event", eventId],
    queryFn: () => dataApi.getEvent(eventId!),
    enabled: Boolean(eventId),
  });
}

export function useIngest() {
  return useMutation({
    mutationFn: (body: IngestRequest) => dataApi.ingest(body),
  });
}

export function useInsight() {
  return useMutation({
    mutationFn: (body: InsightRequest) => dataApi.createInsight(body),
  });
}

export function useTrace(traceId: string | null) {
  return useQuery({
    queryKey: ["trace", traceId],
    queryFn: () => dataApi.getTrace(traceId!),
    enabled: Boolean(traceId),
  });
}

export function useFeedback() {
  return useMutation({
    mutationFn: (body: FeedbackRequest) => dataApi.submitFeedback(body),
  });
}

export function useBudget() {
  return useQuery({
    queryKey: ["budget"],
    queryFn: () => dataApi.getBudget(),
    refetchInterval: 60000,
  });
}

export function useSource(sourceId: string | null) {
  return useQuery({
    queryKey: ["source", sourceId],
    queryFn: () => dataApi.getSource(sourceId!),
    enabled: Boolean(sourceId),
  });
}

export function useChat() {
  return useMutation({
    mutationFn: ({ insightId, question }: { insightId: string; question: string }) =>
      dataApi.chat(insightId, question),
  });
}

export function useInsights(companyId: string | null, role: Role, limit = 8) {
  return useQuery({
    queryKey: ["insights", companyId, role, limit],
    queryFn: () => dataApi.listInsights({ company_id: companyId ?? undefined, role, limit }),
    enabled: Boolean(companyId),
  });
}

export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: () => dataApi.getMetrics(),
    refetchInterval: 60000,
  });
}
