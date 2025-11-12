import os
import bcrypt
import tempfile
import masterPassword

def test_create_and_verify_master_password():
    #temporary directory to avoid overwriting real master hash
    with tempfile.TemporaryDirectory() as tmpdir:
        test_hash_path = os.path.join(tmpdir, ".vaultMaster.hash")

        #temporarily override the global path
        masterPassword.masterHashFile = test_hash_path

        pw = "TestPass123!"
        masterPassword.createMasterPassword(pw)

        assert os.path.exists(test_hash_path), "Hash file not created"

        assert masterPassword.verifyMasterPassword(pw) is True, "Password should verify"

        assert masterPassword.verifyMasterPassword("WrongPass") is False, "Should fail for wrong password"