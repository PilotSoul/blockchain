import hashlib


class POW:
    """
    Class for Proof of Work
    """

    def proof_of_work(self, last_proof) -> int:
        """
        Simple proof of work algorithm:
          - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: previous proof
        :return: current proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the proof. Does hash of last_proof and proof contain 4 leading 0?
        :param last_proof: previous proof
        :param proof: current proof
        :return: correct or not
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"