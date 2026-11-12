import { useOnboarding } from "../../context/OnboardingContext";
import Input from "../ui/Input";
import Select from "../ui/Select";
import Button from "../ui/Button";

type ProfileStepProps = {
  onNext: () => void;
  isSubmitting?: boolean;
};

export function ProfileStep({
  onNext,
  isSubmitting = false,
}: ProfileStepProps) {
  const { data, updateData } = useOnboarding();

  const isFormValid =
    data.firstName.trim().length > 0 &&
    data.birthYear !== "" &&
    data.sex !== "" &&
    data.heightCm !== "" &&
    data.activityLevel !== "";

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!isFormValid || isSubmitting) {
      return;
    }

    onNext();
  }

  return (
    <form
      className="space-y-4"
      onSubmit={handleSubmit}
    >
      <h2 className="text-2xl font-bold">
        Vos informations
      </h2>

      <div>
        <label
          htmlFor="firstName"
          className="mb-1 mt-10 block"
        >
          Prénom
        </label>

        <Input
          id="firstName"
          name="firstName"
          value={data.firstName}
          onChange={(e) =>
            updateData({
              firstName: e.target.value,
            })
          }
          required
        />
      </div>

      <div>
        <label
          htmlFor="birthYear"
          className="mb-1 block"
        >
          Année de naissance
        </label>

        <Input
          id="birthYear"
          name="birthYear"
          type="number"
          min={1900}
          max={new Date().getFullYear()}
          value={data.birthYear}
          onChange={(e) =>
            updateData({
              birthYear: e.target.value,
            })
          }
          required
        />
      </div>

      <div>
        <label
          htmlFor="sex"
          className="mb-1 block"
        >
          Sexe
        </label>

        <Select
          id="sex"
          name="sex"
          value={data.sex}
          onChange={(e) =>
            updateData({
              sex: e.target.value as typeof data.sex,
            })
          }
          required
        >
          <option value="" disabled>
            Sélectionne une option
          </option>

          <option value="male">
            Homme
          </option>

          <option value="female">
            Femme
          </option>

          <option value="other">
            Autre
          </option>
        </Select>
      </div>

      <div>
        <label
          htmlFor="heightCm"
          className="mb-1 block"
        >
          Taille (cm)
        </label>

        <Input
          id="heightCm"
          name="heightCm"
          type="number"
          min={100}
          max={250}
          value={data.heightCm}
          onChange={(e) =>
            updateData({
              heightCm: e.target.value,
            })
          }
          required
        />
      </div>

      <div>
        <label
          htmlFor="activityLevel"
          className="mb-1 block"
        >
          Niveau d’activité
        </label>

        <Select
          id="activityLevel"
          name="activityLevel"
          value={data.activityLevel}
          onChange={(e) =>
            updateData({
              activityLevel: e.target.value as typeof data.activityLevel,
            })
          }
          required
        >
          <option value="" disabled>
            Sélectionne une option
          </option>

          <option value="sedentary">
            Sédentaire
          </option>

          <option value="lightly_active">
            Légèrement actif
          </option>

          <option value="moderately_active">
            Modérément actif
          </option>

          <option value="very_active">
            Très actif
          </option>

          <option value="extremely_active">
            Extrêmement actif
          </option>
        </Select>
      </div>

      <Button
        type="submit"
        variant="primary"
        className="bg-primary font-bold hover:bg-primary-dark mt-4 px-8"
        disabled={!isFormValid || isSubmitting}
      >
        {isSubmitting ? "Enregistrement…" : "Continuer"}
      </Button>
    </form>
  );
}