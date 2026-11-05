import { scoutApi } from "../api";

type VacancyImportCallbacks = {
  loadWorkspace: () => Promise<void>;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export async function runEmployerVacancyImport(
  sourceId: string,
  employerName: string,
  callbacks: VacancyImportCallbacks,
) {
  void callbacks.loadWorkspace().catch(() => undefined);
  try {
    const run = await scoutApi.extractSource(sourceId);
    await callbacks.loadWorkspace();
    callbacks.onNotice(
      employerName + ": " + run.jobs_received + " vacancies imported successfully.",
    );
  } catch (reason) {
    const detail = reason instanceof Error ? reason.message : "An unexpected error occurred.";
    callbacks.onError(
      employerName + " was added, but vacancy import needs attention: " + detail,
    );
    await callbacks.loadWorkspace().catch(() => undefined);
  }
}
