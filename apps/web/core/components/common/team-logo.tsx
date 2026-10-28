export function TeamLogo() {
  return (
    <span className="inline-flex items-center gap-3 text-primary" aria-label="ITPU × Sakura">
      <img src="/sakura/itpu-logo-light.svg" alt="ITPU" width={74} height={36} className="h-9 w-auto dark:hidden" />
      <img src="/sakura/itpu-logo.svg" alt="ITPU" width={74} height={36} className="hidden h-9 w-auto dark:block" />
      <span className="text-lg font-normal text-tertiary" aria-hidden="true">
        ×
      </span>
      <span className="text-lg font-semibold">Sakura</span>
    </span>
  );
}
