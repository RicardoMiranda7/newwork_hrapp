interface ProfileData {
  [key: string]: any;
}

export function isManagerOrOwner(profile: ProfileData, userId: string): boolean {
  if (!profile || !userId) {
    return false;
  }
  return isOwner(profile, userId) || isManager(profile, userId);
}

export function isManager(profile: ProfileData, userId: string): boolean {
  return profile.manager.toString() === userId;
}

export function isOwner(profile: ProfileData, userId: string): boolean {
  return profile.user?.toString() === userId;
}