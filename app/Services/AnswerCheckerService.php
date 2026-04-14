<?php
namespace App\Services;

class AnswerCheckerService
{
    public function check(string $userInput, array $acceptedReadings): bool
    {
        $normalized = $this->normalize($userInput);

        foreach ($acceptedReadings as $reading) {
            if ($normalized === $this->normalize($reading)) {
                return true;
            }
        }
        return false;
    }

    private function normalize(string $input): string
    {
        // Trim, lowercase, strip dots (kun'yomi notation)
        return mb_strtolower(trim(str_replace('.', '', $input)));
    }
}