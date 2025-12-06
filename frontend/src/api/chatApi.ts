import apiClient from "@/api/apiClient";
import type { AxiosResponse } from "axios";

export const chatApi = {
  anonymizeText: (
    text: string
  ): Promise<
    AxiosResponse<{ textAnonymized: string; textSynthetic: string }>
  > =>
    apiClient.post<{ textAnonymized: string; textSynthetic: string }>(
      "/anonymize",
      { text }
    ),
};
