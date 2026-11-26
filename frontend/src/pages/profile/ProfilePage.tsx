import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ActivityLevel } from "../../api/generated/activityLevel";
import { Sex } from "../../api/generated/sex";
import type { UserProfileRead } from "../../api/generated/userProfileRead";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";
import DetailList from "../../components/ui/DetailList";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import { queryKeys } from "../../lib/queryClient";
import { notifySaveResult } from "../../lib/targetUpdate";
import { authService } from "../../services/authService";
import { userService } from "../../services/userService";
import { GoalSection } from "../../components/goal/GoalSection";
import { PageHeader } from "../../components/navigation/PageHeader";
import { RequiredMark } from "../../components/ui/RequiredMark";

const SEX_LABELS: Record<Sex, string> = {
  male: "Homme",
  female: "Femme",
  other: "Autre",
};

const ACTIVITY_LABELS: Record<ActivityLevel, string> = {
  sedentary: "Sédentaire",
  lightly_active: "Légèrement actif",
  moderately_active: "Modérément actif",
  very_active: "Très actif",
  extremely_active: "Extrêmement actif",
};

// Mêmes bornes que le backend (UserProfileUpdate).
const FIRST_NAME_MAX = 100;
const MIN_BIRTH_YEAR = 1900;
const MIN_AGE = 13;
const MIN_HEIGHT_CM = 100;
const MAX_HEIGHT_CM = 250;

// Valeurs du formulaire, gardées en texte pendant la saisie.
type ProfileForm = {
  firstName: string;
  yearOfBirth: string;
  sex: Sex;
  heightCm: string;
  activityLevel: ActivityLevel;
};

function toForm(profile: UserProfileRead): ProfileForm {
  return {
    firstName: profile.first_name ?? "",
    yearOfBirth: String(profile.year_of_birth),
    sex: profile.sex,
    heightCm: String(Number(profile.height_cm)),
    activityLevel: profile.activity_level,
  };
}

// Accepte la virgule comme séparateur décimal ; NaN si vide ou invalide.
function parseDecimal(value: string): number {
  if (value.trim() === "") return NaN;
  return Number(value.replace(",", "."));
}

// Messages d'erreur par champ (null si valide). Le format du prénom est vérifié par le backend.
function validate(form: ProfileForm) {
  const maxYear = new Date().getFullYear() - MIN_AGE;
  const year = Number(form.yearOfBirth);
  const height = parseDecimal(form.heightCm);

  return {
    firstName:
      form.firstName.trim().length > FIRST_NAME_MAX ? `Maximum ${FIRST_NAME_MAX} caractères.` : null,
    yearOfBirth:
      !/^\d{4}$/.test(form.yearOfBirth.trim()) || year < MIN_BIRTH_YEAR || year > maxYear
        ? `Entre ${MIN_BIRTH_YEAR} et ${maxYear}.`
        : null,
    heightCm:
      !Number.isFinite(height) || height < MIN_HEIGHT_CM || height > MAX_HEIGHT_CM
        ? `Entre ${MIN_HEIGHT_CM} et ${MAX_HEIGHT_CM} cm.`
        : null,
  };
}

// Page « Mon profil » : consultation et modification du profil.
export function ProfilePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Même clé que l'accueil : le profil déjà chargé s'affiche immédiatement.
  const profileQuery = useQuery({
    queryKey: queryKeys.profile,
    queryFn: () => userService.getProfile(),
  });
  const userQuery = useQuery({
    queryKey: queryKeys.currentUser,
    queryFn: () => userService.getCurrentUser(),
  });

  // null : mode consultation ; sinon, valeurs du formulaire de modification.
  const [form, setForm] = useState<ProfileForm | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const profile = profileQuery.data;
  const loadError = profileQuery.error?.message ?? userQuery.error?.message ?? null;

  function handleLogout() {
    authService.logout();
    navigate("/login", { replace: true });
  }

  function startEditing() {
    if (!profile) return;
    setForm(toForm(profile));
    setError(null);
  }

  function update<K extends keyof ProfileForm>(key: K, value: ProfileForm[K]) {
    setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
  }

  const fieldErrors = form ? validate(form) : null;
  const canSubmit =
    form !== null && fieldErrors !== null && Object.values(fieldErrors).every((e) => e === null) && !isSubmitting;

  async function handleSubmit(event: React.SubmitEvent) {
    event.preventDefault();
    if (!form || !canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const { target_update, ...updated } = await userService.updateProfile({
        first_name: form.firstName.trim() || null,
        year_of_birth: Number(form.yearOfBirth),
        sex: form.sex,
        height_cm: parseDecimal(form.heightCm),
        activity_level: form.activityLevel,
      });
      // Met à jour le cache : l'accueil affiche aussitôt le nouveau prénom.
      queryClient.setQueryData(queryKeys.profile, updated);
      // Le backend recalcule la cible si la taille, l'âge, le sexe ou l'activité ont changé.
      void queryClient.invalidateQueries({ queryKey: queryKeys.currentTarget });
      notifySaveResult("Votre profil a été mis à jour avec succès.", target_update);
      setForm(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible d’enregistrer votre profil.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const rows = profile
    ? [
        { label: "Prénom", value: profile.first_name?.trim() || "Non défini" },
        { label: "Courriel", value: userQuery.data?.email ?? "…" },
        {
          label: "Année de naissance",
          value: `${profile.year_of_birth} (${new Date().getFullYear() - profile.year_of_birth} ans)`,
        },
        { label: "Sexe", value: SEX_LABELS[profile.sex] },
        { label: "Taille", value: `${Number(profile.height_cm).toLocaleString("fr-CA")} cm` },
        { label: "Niveau d’activité", value: ACTIVITY_LABELS[profile.activity_level] },
      ]
    : [];

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <PageHeader onBack={() => navigate(-1)} />

      <h1>Mon profil</h1>

      {profileQuery.isPending ? (
        <p>Chargement de votre profil…</p>
      ) : loadError ? (
        <p className="text-danger" role="alert">{loadError}</p>
      ) : form && fieldErrors ? (
        <form onSubmit={handleSubmit} className="space-y-4 text-left" noValidate>
          <label className="block">
            <span className="text-sm font-medium">Prénom</span>
            <Input
              value={form.firstName}
              onChange={(event) => update("firstName", event.target.value)}
              maxLength={FIRST_NAME_MAX}
              autoComplete="given-name"
              className="mt-1"
              aria-invalid={fieldErrors.firstName !== null}
            />
            {fieldErrors.firstName && (
              <span className="mt-1 block text-sm text-danger">{fieldErrors.firstName}</span>
            )}
          </label>

          <label className="block">
            <span className="text-sm font-medium">Année de naissance <RequiredMark /></span>
            <Input
              type="text"
              inputMode="numeric"
              value={form.yearOfBirth}
              onChange={(event) => update("yearOfBirth", event.target.value)}
              className="mt-1"
              aria-invalid={fieldErrors.yearOfBirth !== null}
              required
            />
            {fieldErrors.yearOfBirth && (
              <span className="mt-1 block text-sm text-danger">{fieldErrors.yearOfBirth}</span>
            )}
          </label>

          <label className="block">
            <span className="text-sm font-medium">Sexe <RequiredMark /></span>
            <Select
              value={form.sex}
              onChange={(event) => update("sex", event.target.value as Sex)}
              className="mt-1"
            >
              {Object.values(Sex).map((value) => (
                <option key={value} value={value}>{SEX_LABELS[value]}</option>
              ))}
            </Select>
          </label>

          <label className="block">
            <span className="text-sm font-medium">Taille (cm) <RequiredMark /></span>
            <Input
              type="text"
              inputMode="decimal"
              value={form.heightCm}
              onChange={(event) => update("heightCm", event.target.value)}
              className="mt-1"
              aria-invalid={fieldErrors.heightCm !== null}
              required
            />
            {fieldErrors.heightCm && (
              <span className="mt-1 block text-sm text-danger">{fieldErrors.heightCm}</span>
            )}
          </label>

          <label className="block">
            <span className="text-sm font-medium">Niveau d’activité <RequiredMark /></span>
            <Select
              value={form.activityLevel}
              onChange={(event) => update("activityLevel", event.target.value as ActivityLevel)}
              className="mt-1"
            >
              {Object.values(ActivityLevel).map((value) => (
                <option key={value} value={value}>{ACTIVITY_LABELS[value]}</option>
              ))}
            </Select>
          </label>

          {error && <p className="text-danger" role="alert">{error}</p>}

          <div className="grid grid-cols-2 gap-2">
            <Button type="button" variant="secondary" onClick={() => setForm(null)} disabled={isSubmitting}>
              Annuler
            </Button>
            <Button type="submit" className="font-bold" disabled={!canSubmit}>
              {isSubmitting ? "Enregistrement…" : "Enregistrer"}
            </Button>
          </div>
        </form>
      ) : (
        <>
          <Card className="w-full bg-surface">
            <DetailList rows={rows} />
          </Card>


          <Button className="mt-4 w-full font-bold" onClick={startEditing}>
            Modifier
          </Button>

          <GoalSection />

        </>
      )}

      {/* La déconnexion reste disponible même si le profil ne peut pas être chargé. */}
      <button
        type="button"
        onClick={handleLogout}
        className="mt-8 w-full rounded-full py-2 font-bold text-secondary hover:text-secondary-dark"
      >
        Se déconnecter
      </button>
    </main>
  );
}
